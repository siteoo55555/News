from django.shortcuts import render,redirect, HttpResponseRedirect
from django.core.mail import send_mail
from .forms import *
from .models import *
from django.contrib.auth import  authenticate,login,logout
from django.contrib import messages
from django.conf import settings
from django.views import View
from django.urls import reverse
import string
import random



def Login(request):
    form = LoginForm()
    if request.POST:
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            parol = form.cleaned_data['password']
            user = authenticate(request, username=username, password=parol)
            if user is not None:
                login(request, user)
            return redirect('home')
    return render(request, 'login.html', {'form': form})


class Home(View):
    def get(self, request):
        if not request.user.is_authenticated:
            return Login(request)
        chats = Chat.objects.all()
        search = request.GET.get('search')
        chat = None
        id = request.GET.get('id')
        if id:
            chat = Chat.objects.get(id=id)
            for i in chat.chat_messages.all():
                if not i.user==request.user:
                    i.is_read=True
                    i.save()

            a=[]
            for i in chats:
                if i.Admin == request.user or  request.user in i.Admins.all() or request.user in i.members.all():
                    a.append(i)
            if a:
                chats=a
            if search:
                chats=Chat.objects.filter(name__icontains=search)
            chats=chats[::-1]
        m_id = request.GET.get('message_id')
        sms_obj = None
        if m_id:
            sms_obj = Messages.objects.get(id=m_id)
        return render(request, 'home.html',{'chats':chats,'chat':chat, 'sms_obj': sms_obj})

    def post(self, request):
        if request.user.is_authenticated:
            sms_id = request.POST.get['sms']
            sms_id = Messages.objects.get(id=sms_id)
            if request.user in sms_id.likes.all():
                sms_id.likes.remove(request.user)
            else:
                sms_id.likes.add(request.user)    
            sms = request.POST.get('sms')
            chat_id = request.POST.get('id')
            
            if chat_id:
                if request.POST.get('message_id'):
                    pass
                if sms:
                    Messages.objects.create(
                        sms = sms,
                        user = request.user,
                        chat = Chat.objects.get(id=int(chat_id))
                    )
                return redirect(reverse('home') + f'?id={chat_id}')
            azo = request.POST.get('azo')
            if azo:
                chat = Chat.objects.get(id=azo)
                chat.members.add(request.user)
                chat.save()
            return redirect(reverse('home') + f'?chat_id={azo}')
        return Login(request)

def delete_sms(request,id,message_id):
    sms=Messages.objects.get(id=message_id)
    sms.delete()
    chat=Chat.objects.get(id=id)
    chats=Chat.objects.all()
    return render(request,'home.html',{'chat':chat,'chats':chats})


def register(request):
    r = UserForm()
    if request.POST:
        r = UserForm(request.POST)
        if r.is_valid():
            user = r.save()
            parol = r.cleaned_data['password']
            user.set_password(parol)
            user.save()
            return redirect('home')
    return render(request, 'user.html', {'r': r})
class Confirm(View):
    def get(self, request):
        return render(request, 'confirm.html')
    def post(self, request):
        code = request.POST.get('code', 0)
        if code:
            a=request.user.user_codes.last()
            if a.code == int(code) and a.expired_time>=timezone.now():
                request.user.active=True
                request.user.save()
                messages.success(request, s='You are confirmed!👍👌')

                return redirect('home')
            else:
                messages.info(request, 'There is error code :)😐')
        else:
            messages.info(request, 'Your email is invalid!😐')
        
class Create_Group(View):
    def get(self, request):
        form = ChatNameForm()
        return render(request, 'name.html', {'form':form})
    def post(self, request):
            form = ChatNameForm(request.POST)
            if form.is_valid():
                group = form.save(commit=False)
                group.tur = 'guruh'
                group.save()
                return redirect('add', group.id)

class Add_Members(View):
    def get(self, request, id):
        form = ChatMembersForm()
        return render(request, 'add.html', {'form': form})
    def post(self, request, id):
        chat = Chat.objects.get(id=id)
        form = ChatMembersForm(request.POST)
        if form.is_valid():
            azolar = request.POST.getlist('members')
            for i in azolar:
                user = User.objects.get(id=i)
                chat.members.add(user)
            chat.save()
        return redirect(reverse('home') + f'?id={id}')

class Remove_Members(View):
    def get(self, request, id):
        form = ChatMembersForm()
        return render(request, 'remove.html', {'form': form})
    def post(self, request, id):
        chat = Chat.objects.get(id=id)
        form = ChatMembersForm(request.POST)
        if form.is_valid():
            azolar = request.POST.getlist('members')
            for i in azolar:
                user = User.objects.get(id=i)
                chat.members.remove(user)
            chat.save()
        return redirect(reverse('home') + f'?id={id}')

class Create_Channel(View):
    def get(self, request):
        form = ChatNameForm()
        return render(request, 'channel.html', {'form':form})
    def post(self, request):
        form = ChatNameForm(request.POST)
        if form.is_valid():
            group = form.save(commit=False)
            group.tur = 'guruh'
            group.save()
            return redirect('add', group.id)

def dino(request):
    ...
    return render(request, 'dino.html')

def help(request):
    ...
    return render(request, 'help.html')

class Change_Password(View):
    def get(self, request):
        form = PasswordForm()
        return render(request, 'change.html', {'form': form})
    def post(slef, request):
        form = PasswordForm(request.POST)
        p_1 = form.data['old_password']
        p_2 = form.data['new_password']
        user = request.user
        if user.check_password(p_1):
            user.set_password(p_2)
            user.save()
        return redirect('home')
class User_Edit(View):
    def get(self, request):
        form = UserEditForm(instance=request.user)
        return render(request, 'user_edit.html', {'form': form})
    def post(self, request):
        form = UserEditForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('home')

class Profile_Edit(View):
    def get(self, request):
        form = UserEditForm(instance=request.user)
        return render(request, 'user_edit.html', {'form': form})
    def post(self, request):
        form = UserEditForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('home')


def create_profile(request):
    form = ProfileForm()
    if request.POST:
        form = ProfileForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')

def calculator(request):
    ...
    return render(request, 'calc.html')

def quiz(request):
    ...
    return render(request, 'quest.html')
def typing_test(request):
    ...
    return render(request, 'typing.html')


def tic_tac_toe(request):
    ...
    return render(request, 'tic.html')

def flappy_bird(request):
    ...
    return render(request, 'stack.html')

def memory(request):
    ...
    return render(request, 'memory.html')

def pinball(request):
    ...
    return render(request, 'ball.html')

def mouse_tap(request):
    ...
    return render(request, 'tap.html')

def snake(request):
    ...
    return render(request, 'snake.html')

def chatbot(request):
    ...
    return render(request, 'index.html')

def translator(request):
    ...
    return render(request, 'translate.html')

class Create_Profile(View):
    def get(self, request):
        form = ProfileForm()
        return render(request, 'profile.html', {'form':form})
    def post(self, request):
        form = ProfileForm(request.POST)
        if form.is_valid():
            form.save()
        return redirect('home')



def profile_image_create(request):
    form=PhotoForm()
    if request.POST:
        form=PhotoForm(request.POST,request.FILES)
        if form.is_valid():
            p=Profile.objects.get(user=request.user)
            Photo.objects.create(
                Profile=p,
                image=form.cleaned_data['image']
            )
            imgs=Photo.objects.all()
            return render(request,'imgs.html',{'imgs':imgs,'form':form})
    return render(request,'imgs.html',{'imgs':imgs,'form':form})


def profile_image_delete(request,id):
    photo=Photo.objects.get(id=id)
    photo.delete()
    return redirect('profile_img_create')


class Create_Friend_Chat(View):
    def get(self, request):
        users=User.objects.all()
        return render(request,'friend.html',{'users':users})
    def post(self, request):
        form=Create_Friend_ChatForm(request.POST,files=request.FILES)
        user=User.objects.get(id = id)
        if form.is_valid:
            chat = Chat.objects.create(
            status='Friends'
            )
            chat.members.add(request.user)
            chat.members.add(user)
            chat.save()
            return redirect('home')

def about(request):
    ...
    return render(request, 'icons.html')


def Logout(request):
    logout(request)
    return redirect('home')


def create_chat_link(request,id):
    chat = Chat.objects.get(id=id)
    random_string = ''.join(random.choices(string.ascii_letters + string.digits, k=20))
    a = 'http://127.0.0.1:8000/'+random_string+'www.com'
    Chat_Link.objects.create(
        chat=chat,
        url=a
    )
    return redirect('home')

def delete_sms(request,id,sms_id):
    sms=Messages.objects.get(id=sms_id)
    sms.delete()
    chat=Chat.objects.get(id=id)
    chats=Chat.objects.all()
    return render(request,'home.html',{'chat':chat,'chats':chats})



def edit_function(request, sen):
    news =Chat.objects.get(id=sen)
    form = ChatNameForm(instance=news)
    if request.POST:
        form = ChatNameForm(request.POST, files=request.FILES, instance=news)
        if form.is_valid():
            form.save()
            return redirect('home')
    return render(request, 'edit.html', {'form': form})

def delete(request, me):
    chat_delete = Chat.objects.get(id=me)
    chat_delete.delete()
    return redirect('home')




            # send_mail(
            #     f'Salom, {a.username}',
            #     f'Sizning tasdiqlash kodingiz - {a.user_codes.last().code}',
            #     settings.EMAIL_HOST_USER,
            #     [a.email],
            #     fail_silently=False
            # )
            # messages.info(request, 'Sizga kod yubordik')


# def create_chat_f(request):
#     users=User.objects.all()
#     if request.GET:
#         user=User.objects.get(id = id)
#         if request.POST:
#             form=Create_Friend_ChatForm(request.POST,files=request.FILES)
#             if form.is_valid():
#                 chat = Chat.objects.create(
#                     status='Friends'
#                 )
#                 chat.members.add(request.user)
#                 chat.members.add(user)
#                 chat.save()
#                 return redirect('home')
#         return render(request,'friend.html',{'users':users})
# class Users(View):
#     def get(self, request):
#         r = UserForm()
#         return render(request, 'user.html', {'r': r})
#     def post(self, request):
#         r = UserForm(request.POST)
#         if r.is_valid():
#             a = r.save(commit=False)
#             a.set_password(r.cleaned_data['password'])
#             a.save()
#             login(request, a)
#             send_mail(
#                 f'Salom, {a.username}',
#                 f'Sizning tasdiqlash kodingiz - {a.user_codes.last().code}',
#                 settings.EMAIL_HOST_USER,
#                 [a.email],
#                 fail_silently=False
#             )
#             messages.info(request, 'Sizga kod yubordik')
#             return redirect('home')



# old function

# def user_edit(request):
#     form = UserEditForm(instance=request.user)
#     if request.POST:
#         form = UserEditForm(request.POST, instance=request.user)
#         if form.is_valid():
#             form.save()
#             return redirect('home')
#     return render(request, 'user_edit.html', {'form': form})


# old function

# def change_password(request):
#     form = PasswordForm()
#     if request.POST:
#         form = PasswordForm(request.POST)
#         p_1 = form.data['password_1']
#         p_2 = form.data['password_2']
#         user = request.user
#         if user.check_password(p_1):
#             user.set_password(p_2)
#             user.save()
#             return redirect('home')
    # return render(request, 'change.html', {'form': form})

# old function

# def login(request):
#     form = LoginForm()
#     if request.POST:
#         form = LoginForm(request.POST)
#         if form.is_valid():
#             a = request.POST['username']
#             b = request.POST['password']
#             f = authenticate(request, username=a, password=b)
#             print(f)
#             if f is not None:
#                 login(request, f)
#                 return redirect('home')
#     return render(request, "index.html", {'form': form})



# old function

# def create_channel(request):
#     form = ChatNameForm()
#     if request.POST:
#         form = ChatNameForm(request.POST)
#         if form.is_valid():
#             group = form.save(commit=False)
#             group.tur = 'guruh'
#             group.save()
#             return redirect('add', group.id)
#     return render(request, 'channel.html', {'form':form})

# def add_members(request, id):
#     chat = Chat.objects.get(id=id)
#     form = ChatMembersForm()
#     if request.POST:
#         form = ChatMembersForm(request.POST)
#         if form.is_valid():
#             azolar = request.POST.getlist('members')
#             for i in azolar:
#                 user = User.objects.get(id=i)
#                 chat.members.add(user)
#             chat.save()
#             return redirect('home')
#     return render(request, 'add.html', {'form': form})



# old function

# def create_group(request):
#     form = ChatNameForm()
#     if request.POST:
#         form = ChatNameForm(request.POST)
#         if form.is_valid():
#             group = form.save(commit=False)
#             group.tur = 'guruh'
#             group.save()
#             return redirect('add', group.id)
#     return render(request, 'name.html', {'form':form})




# old function

# def home(request):
#     chats = Chat.objects.all()
#     chat = None
#     if request.GET:
#         id = request.GET.get('chat_id')
#         chat = Chat.objects.get(id=id)
#     if request.POST:
#         sms = request.POST.get('sms')
#         chat_id = request.POST.get('chat_id')
#         Messages.objects.create(
#             sms = sms,
#             user = request.user,
#             chat = Chat.objects.get(id=int(chat_id))
#         )
#     return render(request, 'home.html', {'chats': chats, 'chat': chat})





# old function
# def confirm(request):
#     if request.POST:
#         code = request.POST.get('code', 0)
#         if code:
#             a=request.user.user_codes.last()
#             if a.code == int(code) and a.expired_time>=timezone.now():
#                 request.user.active=True
#                 request.user.save()
#                 messages.success(request, 'Siz tasdiqlandingiz  !')

#                 return redirect('home')
#             messages.warning(request, 'Sizda xato kod bor :)')
#     return render(request, 'confirm.html')