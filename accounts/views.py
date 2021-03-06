from django.shortcuts import render
import psycopg2
import tempfile
import shutil
from django.core.files.storage import FileSystemStorage
from django.core.files.storage import default_storage

from PIL import Image

import sys
import hashlib





# LOGGING = {
#     'version': 1,
#     'handlers': {
#         'console': {
#             'class': 'logging.StreamHandler',
#             'stream': sys.stdout,
#         }
#     },
#     'root': {
#         'handlers': ['console'],
#         'level': 'INFO'
#     }
# }
import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)
# logging.config.dictConfig(LOGGING)
# logging.info('Hello')

FILE_UPLOAD_DIR = '/media'


# Create your views here.
def login(request):
    if 'Logged In' in request.session and request.session['Logged In'] == True:
        return render(
            request,
            'accounts/welcome.html',
            {
                "message": " ",
            }
        )

    request.session['Logged In'] = False
        # return render(
        #     request,
        #     'accounts/Welcome.html',
        #     {
        #         "message": " ",
        #     }
        # )

    return render(
        request,
        'accounts/login.html',
        {
            "message": " ",
        }
    )

def logout(request):
    request.session['Logged In'] = False
    del request.session['user_id']
    del request.session['user_name']

    return render(
        request,
        'accounts/login.html',
        {
            "message": " ",
        }
    )


def signup(request):

    return render(
        request,
        'accounts/signup.html',
        {}
    )

def register(request):
    username = request.POST['username']
    password = request.POST['password']
    email = request.POST['email']
    print(username)
    print(password)
    passwordhash = hashlib.sha1(password.encode())
    passwordhash = passwordhash.hexdigest()

    print(passwordhash)
    cursor = connection.cursor()
    try :
        cursor.execute("INSERT into account(username,password,email) values(%s,%s,%s) returning user_id",(str(username),str(passwordhash),str(email),))
        connection.commit()
        user_id = cursor.fetchone()
    except:
        logging.debug('A user was unable to sign up')
        return render(
            request,
            'accounts/signup.html',
            {
                "message": "We already have account with this email id. Try logging in."
            }
        )
    logging.debug('A user signed up')
    return render(
        request,
        'accounts/login.html',
        {
            "message" : "you are in our database.Login to continue"
        }
    )
def welcome(request):
    if (request.session['Logged In'] == True):
        return render(
            request,
            'accounts/welcome.html',
            {}
        )
    return render(
        request,
        'accounts/login.html',
        {}
    )

def main_menu(request):
    # Receives POST from login.html Form
    print(connection)
    if request.method == 'POST':
        useremail = request.POST['useremail']
        userpass = request.POST['password']
        print(useremail)
        print(userpass)
        userpass = hashlib.sha1(userpass.encode())
        userpass = userpass.hexdigest()
        cursor = connection.cursor()
        print(cursor)
        cursor.execute("select user_id, username from account where email = %s and password = %s", (str(useremail),str(userpass),))
        #cursor.execute('select * from account')
        data = cursor.fetchone()
        user_id = data[0]
        user_name = data[1]
        if user_name is not None:
            logger.debug('A user Logged In')
            logger.info('A user Logged In')
            request.session['Logged In'] = True
            request.session['user_name'] = user_name
            request.session['user_id'] = user_id
            return render(
                request,
                'accounts/welcome.html',
                {
                    "name" : user_name
                }
            )

        #cursor.close()

        return render(
            request,
            'accounts/login.html',
            {
                "message" : "wrong credentials! Try again"
            }
        )

    else:
        return render(
            request,
            'accounts/login.html',
            {}
        )

def upload_image(request):
    folder='media/'
    if request.method == 'POST' and request.FILES['image']:
        myfile = request.FILES['image']
        fs = FileSystemStorage(location=folder) #defaults to   MEDIA_ROOT
        filename = fs.save(myfile.name, myfile)

        print(filename)

        #file_url = fs.url(filename)
        newfile = Image.open('media/'+myfile.name)
        print(newfile)
        x, y = newfile.size
        size = max(256, int(x), int(y))
        squared_image = Image.new('RGBA', (size, size), (1, 1, 1, 1))
        squared_image.paste(newfile, (int((size - x) / 2), int((size - y) / 2)))
        squared_image.show()
        #filename2 = fs.save("me_rutgers_sq.jpeg", newfile)
        #file_url2 = fs.url(filename2)
        cursor = connection.cursor()
        cursor.execute("INSERT into imagelog(user_id,image_path) values(%s,%s) ",(str(request.session['user_id']),str(filename),))
        connection.commit()
        logging.debug('user squariified the image')
        cursor.execute('select image_path from imagelog where user_id = %s',(str(request.session['user_id']),))
        image_names = cursor.fetchall()
        image_names = list(sum(image_names, ()))
        html = "you have squrified these images--<br>"
        for name in image_names:
            html += "<img src=/media/"+str(name)+" height='100' width='100'><br>"
        return render(request, 'accounts/show_image.html', {
            'html': html
        })
    else:
         return render(request, 'accounts/show_image.html')

import matplotlib.pyplot as plt
from django.http import HttpResponse

def get_image(request):
    cursor = connection.cursor()
    cursor.execute("select value from testing")
    # cursor.execute('select * from account')
    values = cursor.fetchall()
    values = list(sum(values, ()))

    plt.plot(values)

    # plt.plot([1, 2, 3, 4, 5, 6])
    plt.ylabel('some numbers')
    plt.savefig('media/image.png')
    # cursor.close()
    # connection.close()
    # Send buffer in a http response the the browser with the mime type image/png set
    return render(request, 'accounts/show_graph.html', {
        'file_url': "/media/image.png"
    })
