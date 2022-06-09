from django import forms


class RegisterForm(forms.Form):
    username = forms.CharField(label='User Name')
    pw = forms.CharField(widget=forms.PasswordInput, label="Password")
    pw2 = forms.CharField(widget=forms.PasswordInput,label="Retype Password")


class LoginForm(forms.Form):
    username = forms.CharField(label='User Name')
    pw = forms.CharField(widget=forms.PasswordInput,label="Password")


class PostThread(forms.Form):
    threadname = forms.CharField(label="Thread Name:")
    threadcontent = forms.CharField(widget=forms.Textarea, label="Discussion:")


class PostReply(forms.Form):
    replycontent = forms.CharField(widget=forms.Textarea, label="reply")


class AddFriend(forms.Form):
    addfriend = forms.CharField(label="", required=False)


class AddTrigger(forms.Form):
    add_trigger = forms.CharField(label="", required=False)


class RemoveTrigger(forms.Form):
    remove_trigger = forms.CharField(label="", required=False)


class SendChat(forms.Form):
    message = forms.CharField(label="", required=False)


class ProcessChatData(forms.Form):
    username = forms.CharField(label='')
    room_id = forms.CharField(label='')
    message = forms.CharField(label='')
