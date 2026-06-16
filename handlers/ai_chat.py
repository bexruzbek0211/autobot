   import requests
   from telegram import Update
   from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

   OPENAI_API_KEY = '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'

   def get_ai_response(question):
       headers = {
           'Authorization': f'Bearer {OPENAI_API_KEY}',
           'Content-Type': 'application/json',
       }
       data = {
           'model': 'gpt-3.5-turbo',
           'messages': [{'role': 'user', 'content': question}],
       }
       response = requests.post('https://api.openai.com/v1/chat/completions', headers=headers, json=data)
       answer = response.json()['choices'][0]['message']['content']
       return answer

   def start(update: Update, context: CallbackContext) -> None:
       update.message.reply_text('Salom! Savolingizni bering.')

   def answer(update: Update, context: CallbackContext) -> None:
       user_question = update.message.text
       ai_response = get_ai_response(user_question)
       update.message.reply_text(ai_response)

   def main() -> None:
       updater = Updater("YOUR_TELEGRAM_BOT_TOKEN")

       updater.dispatcher.add_handler(CommandHandler("start", start))
       updater.dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, answer))

       updater.start_polling()
       updater.idle()

   if __name__ == '__main__':
       main()
   
