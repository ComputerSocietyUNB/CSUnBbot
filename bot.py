import os
import sys
import logging
import telegram
import subprocess

from config import get_token
from telegram import Bot, User
from telegram.ext import Updater, CommandHandler, Dispatcher,\
	MessageHandler, Filters, ConversationHandler

class Chatterbot:

	def __init__(self, token):
		self.REPO = range(1)
		logging.basicConfig(
			format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
			level=logging.INFO,
		)
		self.logger = logging.getLogger("LOG")
		self.app = Bot(token)
		self.updater = Updater(token)
		self.dispatcher = self.updater.dispatcher

		start_handler = CommandHandler("start", self.start)
		self.dispatcher.add_handler(start_handler)

		# add_repo_handler = CommandHandler("add", self.add_repo, pass_args=True)
		# self.dispatcher.add_handler(add_repo_handler)

		add_repo_handler = ConversationHandler(
			entry_points=[CommandHandler('add', self.add_repo, pass_args=True)],
			states={
				self.REPO: [MessageHandler(Filters.text, self.add_get_repo)]
			},
			fallbacks=[CommandHandler('cancel', self.cancel)]
		)
		self.dispatcher.add_handler(add_repo_handler)

		remove_repo_handler = ConversationHandler(
			entry_points=[CommandHandler('remove', self.remove_repo, pass_args=True)],
			states={
				self.REPO: [MessageHandler(Filters.text, self.rm_get_repo)]
			},
			fallbacks=[CommandHandler('cancel', self.cancel)]
		)
		self.dispatcher.add_handler(remove_repo_handler)
		
		update_handler = ConversationHandler(
			entry_points=[CommandHandler('update', self.update, pass_args=True)],
			states={
				self.REPO: [MessageHandler(Filters.text, self.upd_get_repo)]
			},
			fallbacks=[CommandHandler('cancel', self.cancel)]
		)
		self.dispatcher.add_handler(update_handler)

		run_handler = ConversationHandler(
			entry_points=[CommandHandler('run', self.run, pass_args=True)],
			states={
				self.REPO: [MessageHandler(Filters.text, self.run_get_repo)]
			},
			fallbacks=[CommandHandler('cancel', self.cancel)]
		)
		self.dispatcher.add_handler(run_handler)

		download_handler = ConversationHandler(
			entry_points=[CommandHandler('download', self.download, pass_args=True)],
			states={
				self.REPO: [MessageHandler(Filters.text, self.download_get_repo)]
			},
			fallbacks=[CommandHandler('cancel', self.cancel)]
		)
		self.dispatcher.add_handler(download_handler)

		help_handler = CommandHandler("help", self.help)
		self.dispatcher.add_handler(help_handler)


	def start(self, bot, update):
		"""
		Start command to receive /start message on Telegram.
		"""
		print(update.message["chat"])
		start_text = "Eu sou o bot da IEEE Computer Society UnB " \
			"e gerencio o aplicativos da instituição. " \
			"Digite /help para saber mais sobre meus comandos."
		bot.send_message(chat_id=update.message.chat_id, text=start_text)
		
		start_text = "Agora vamos lá. Em que posso ajudá-lo?"
		bot.send_message(chat_id=update.message.chat_id, text=start_text)
		return 

	def add_repo(self, bot, update, args):
		admin = update.message["chat"]["username"]
		if not self.check_admin_permission(admin, bot, update):
			bot.send_message(chat_id=update.message.chat_id, text="Você não tem autorização para esta ação.")
			return False
		if args == []:
			msg = "Qual repositório você quer adicionar?"
			bot.send_message(chat_id=update.message.chat_id, text=msg)
			return self.REPO 
		else:
			for repo in args:
				try:
					subprocess.run(
						f'git clone https://github.com/ComputerSocietyUNB/{repo} repos/{repo}',
						shell=True
					)
					update.message.reply_text(f'Repositório {repo} baixado com sucesso.')

				except:
					update.message.reply_text(f'Não achei o repositório {repo}.')
				print(repo)
			return ConversationHandler.END

	def add_get_repo(self, bot, update):
		repo = update.message.text.split()
		self.add_repo(bot, update, repo)

		return ConversationHandler.END

	def cancel(self, bot, update):
		print("Pass")
		return ConversationHandler.END

	def remove_repo(self, bot, update, args):
		admin = update.message["chat"]["username"]
		if not self.check_admin_permission(admin, bot, update):
			bot.send_message(chat_id=update.message.chat_id, text="Você não tem autorização para esta ação.")
			return False
		if args == []:
			msg = "Qual repositório você quer adicionar?"
			bot.send_message(chat_id=update.message.chat_id, text=msg)
			return self.REPO 
		else:
			for repo in args:
				try:
					subprocess.run(
						f'rm -rf repos/{repo}',
						shell=True
					)
					update.message.reply_text(f'Repositório {repo} removido com sucesso.')

				except:
					update.message.reply_text(f'Repositório {repo} não encontrado.')
				print(repo)
			return ConversationHandler.END

	def rm_get_repo(self, bot, update):
		repo = update.message.text.split()
		self.remove_repo(bot, update, repo)

		return ConversationHandler.END

	def update(self, bot, update, args):
		user = update.message["chat"]["username"]
		if not self.check_user_permission(user, bot, update):
			bot.send_message(chat_id=update.message.chat_id, text="Você não tem autorização para esta ação.")
			return False
		if args == []:
			msg = "Qual repositório você quer atualizar?"
			bot.send_message(chat_id=update.message.chat_id, text=msg)
			return self.REPO 
		else:
			for repo in args:
				try:
					msg = subprocess.run(
						f'cd repos/{repo} && git pull origin master',
						shell=True
					)
					update.message.reply_text(f'Ação finalizada com sucesso.')

				except Exception as e:
					update.message.reply_text(f'Repositório {repo} não encontrado. {e}')
				print(repo)
			return ConversationHandler.END

	def upd_get_repo(self, bot, update):
		repo = update.message.text.split()
		self.update(bot, update, repo)

		return ConversationHandler.END

	def run(self, bot, update, args):
		user = update.message["chat"]["username"]
		if not self.check_user_permission(user, bot, update):
			bot.send_message(chat_id=update.message.chat_id, text="Você não tem autorização para esta ação.")
			return False
		if args == []:
			msg = "Qual repositório você quer atualizar?"
			bot.send_message(chat_id=update.message.chat_id, text=msg)
			return self.REPO 
		else:
			for repo in args:
				try:
					subprocess.run(
						f'cd repos/{repo} && . venv/bin/activate && inv run',
						shell=True
					)
					update.message.reply_text(f'Ação finalizada com sucesso.')

				except Exception as e:
					update.message.reply_text(f'Repositório {repo} não encontrado. {e}')
				print(repo)
			return ConversationHandler.END

	def run_get_repo(self, bot, update):
		repo = update.message.text.split()
		self.update(bot, update, repo)
		return ConversationHandler.END

	def download(self, bot, update, args):
		user = update.message["chat"]["username"]
		chat_id = update.message.chat_id
		if not self.check_user_permission(user, bot, update):
			bot.send_message(chat_id=chat_id, text="Você não tem autorização para esta ação.")
			return False
		if args == []:
			msg = "Qual repositório você quer atualizar?"
			bot.send_message(chat_id=chat_id, text=msg)
			return self.REPO 
		else:
			for repo in args:
				try:
					bot.send_document(chat_id=chat_id, document=open(f'repos/{repo}/data_mine/amazon/p0.txt', 'rb'))
					bot.send_document(chat_id=chat_id, document=open(f'repos/{repo}/data_mine/amazon/p1.txt', 'rb'))
					bot.send_document(chat_id=chat_id, document=open(f'repos/{repo}/data_mine/amazon/p2.txt', 'rb'))
					bot.send_document(chat_id=chat_id, document=open(f'repos/{repo}/data_mine/amazon/n0.txt', 'rb'))
					bot.send_document(chat_id=chat_id, document=open(f'repos/{repo}/data_mine/amazon/n1.txt', 'rb'))
					bot.send_document(chat_id=chat_id, document=open(f'repos/{repo}/data_mine/amazon/n2.txt', 'rb'))
					update.message.reply_text(f'Ação finalizada com sucesso.')

				except Exception as e:
					update.message.reply_text(f'Repositório {repo} não encontrado. {e}')
				print(repo)
			return ConversationHandler.END

	def download_get_repo(self, bot, update):
		repo = update.message.text.split()
		self.update(bot, update, repo)
		return ConversationHandler.END
		

	def help(self, bot, update):
		msg = "/add - Add new Github repository\n" \
			"/remove - Remove Github repository\n" \
			"/update - Update Github repository\n" \
			"/run - Run main executable\n" \
			"/download - Download generated files from repository (if available)\n" \
			"/help - List all commands\n" \
			"/info - Show more information about the bot"
		bot.send_message(chat_id=update.message.chat_id, text=msg)
		return True

	def check_admin_permission(self, admin, bot, update, admin_file="admin.txt"):
		with open(admin_file, 'r') as adm_file:
			all_adms = adm_file.read().splitlines()
			if admin in all_adms:
				return True
		return False

	def check_user_permission(self, user, bot, update, user_file="user.txt"):
		with open(user_file, 'r') as usr_file:
			all_usrs = usr_file.read().splitlines()
			if user in all_usrs:
				return True
		# bot.send_message(chat_id=update.message.chat_id, text="Você não tem autorização para esta ação.")
		return self.check_admin_permission(user, bot, update)

	def run_bot(self):
		# Start the Bot
		self.updater.start_polling()

		# Run the bot until you press Ctrl-C or the process receives SIGINT,
		# SIGTERM or SIGABRT. This should be used most of the time, since
		# start_polling() is non-blocking and will stop the bot gracefully.
		self.updater.idle()
		return 0


if __name__ == "__main__":
	# Variables set on Heroku
	TOKEN = os.environ.get("TOKEN")
	NAME = os.environ.get("NAME")
	# Port is given by Heroku
	PORT = os.environ.get("PORT")
	if TOKEN is not None:
		bot = Chatterbot(TOKEN)
		bot.updater.start_webhook(
			listen="0.0.0.0",
			port=int(PORT),
			url_path=TOKEN)
		bot.updater.bot.set_webhook(f"https://{NAME}.herokuapp.com/{TOKEN}")
		bot.updater.idle()

	# Run on local system once detected that it's not on Heroku
	else:
		try:
			token = get_token()["token"]
			x = Chatterbot(token).run_bot()
		except FileNotFoundError:
			print("Configuration file not found.")
			sys.exit(1)
