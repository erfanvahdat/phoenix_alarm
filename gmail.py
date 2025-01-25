

import pandas as pd
from email import encoders
import email, smtplib, ssl
from termcolor import colored
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from colorama import Fore
def gmail(ticker,pos_type,utils=None,status=None,attach_file=None ):

    # subject = f"RSI Alert for {Fore.GREEN}{ticker}+USDT {Fore.WHITE} ON {Fore.MAGENTA}{pos_type}"
    subject = f'RSI Alert for {ticker}USDT ON {pos_type}'
    body = """\ 
        This is an email with attachment sent from Python
        <b>This line is bold.</b>
        <br>
        Another line in the email body.
    """
    name = 'CRPYTO'
    value =20000
    # if type == "SHORT" :
    #     color_position = "#FF5733"
    # if type == "LONG" :
    #     color_position = "#088F8F"


# <div style="width: 200px; height: 200px; background-color: {color_position}; text-align: center; padding-top: 10px;">
#                 <span style="color: #A020F0; font-size: 25px;"> -->{market}<-- </span><br><br>
#                     <span style="color: #000000 ; font-size: 18px;">{symbol.upper()} </span><br>
#                     <span style="color: #000000 ; font-size: 18px;">{type.upper()} </span><br>
#                     <span style="color: #000000 ; font-size: 18px;">{date} </span><br>



    market = "CRYPTO"
    html_template = f"""
        <html>  
            <head></head>
            <body>
                
            <div>
            <span style="color: #000000 ; font-size: 18px;">Hello </span><br>
            
                <div/>
            </body>
        </html>
        """
    sender_email = 'erfanvahdat.6@gmail.com'
    password = 'rprr drvl hcls urqe'
    receiver_email = 'erfanvahdat.6@gmail.com'
    
                    #   'sina.h.pilot1378@gmail.com']
    
    # Create a multipart message and set headers
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject
    message["Bcc"] = receiver_email  # Recommended for mass emails

    # Add body to email
    message.attach(MIMEText(html_template, "html"))


    filename = f"{attach_file}.png"  # In same directory as script

    # ------------------attachment to the gmail------------------------------------
    if attach_file != None:
        # Open PDF file in binary mode
        with open(filename, "rb") as attachment:
            # Add file as application/octet-stream
            # Email client can usually download this automatically as attachment
            part = MIMEBase("application", "octet-stream")
            part.set_payload(attachment.read())

        # Encode file in ASCII characters to send by email    
        encoders.encode_base64(part)

        # Add header as key/value pair to attachment part
        part.add_header(
            "Content-Disposition",
            f"attachment; filename= {filename}",
        )

        # Add attachment to message and convert message to string
        message.attach(part)
    # ------------------------------------------------------


    # Log in to server using secure context and send email
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(sender_email, password)
        # for i in receiver_email:
        server.sendmail(sender_email, receiver_email,  message.as_string())

    return print(colored(f'sedning Signals to{receiver_email}',color='light_blue'))




gmail(ticker='BTC',pos_type = 'short')
