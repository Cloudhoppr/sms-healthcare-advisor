from flask import Flask, request
from langchain.agents import create_agent
from twilio.twiml.messaging_response import MessagingResponse

MODEL = "model"

sms_chain = create_agent(
    model = MODEL, 
    tools=None
    )

app = Flask(__name__)


'''@app.route("/sms", methods=['GET', 'POST'])
def sms():
    resp = MessagingResponse()
    inb_msg = request.form['Body'].lower().strip()
    output = sms_chain.predict(sms_input=inb_msg)
    print(output)
    resp.message(output)
    return str(resp)

if __name__ == "__main__":
    app.run(debug=True)'''