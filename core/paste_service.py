from models import Paste
from rx import Observable, Observer

class PasteService(Observer):
	users = None
	def on_next(self):
		self.users = [a.json() for a in UserModel.query.all()]

	def on_completed(self):
		return self.users
	def on_error(self):
		return {"message":"Error occured"}