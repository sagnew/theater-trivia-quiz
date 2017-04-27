from random import choice, shuffle

from flask import Flask, request, session
from twilio.twiml.messaging_response import MessagingResponse
from requests import get

# The session object makes use of a secret key.
SECRET_KEY = 'a secret key'
app = Flask(__name__)
app.config.from_object(__name__)

@app.route("/sms", methods=['POST'])
def quiz():
    # Grab the state from the session.
    quiz_state = session.get('quiz_state', 'new_question')
    response = MessagingResponse()

    if quiz_state == 'answering':
        # Determine the correct answer to the question.
        correct_answer = session.get('correct_answer')

        # Retrieve the user's current answer.
        current_answer = request.form['Body'].lower().strip()

        if current_answer == correct_answer:
            msg = 'That is correct! :) Reply to this for another question.'
            response.message(msg)
        else:
            msg = 'That is incorrect! :( Reply to this for another question.'
            response.message(msg)

        session['quiz_state'] = 'new_question'
    elif quiz_state == 'new_question':
        quiz_url = 'https://opentdb.com/api.php?amount=10&category=13'
        question_set = get(quiz_url).json()['results']

        print(question_set)

        new_question = choice(question_set)
        print(new_question)

        answers = []
        answers.append(new_question['correct_answer'])
        answers.extend(new_question['incorrect_answers'])
        shuffle(answers)

        message = new_question['question'] + '\n'
        for answer in answers:
            message += '\n{}\n'.format(answer)
        print(message)
        response.message(message)

        session['correct_answer'] = new_question['correct_answer'].lower().strip()
        session['quiz_state'] = 'answering'

    return str(response)

if __name__ == "__main__":
    app.run(debug=True)
