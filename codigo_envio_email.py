import smtplib
import email.message

def send_email():
    corpo_email = '''
    <p>Teste</p>
    <p>Só passando uma mensagem para saber se realmente está funcionando...</p>
    '''
    # Digite aki acima a mensagem a ser enviada

    msg = email.message.Message()
    msg['Subject'] = 'Email teste.' # Assunto do email
    msg['From'] = 'gustavosymoons@gmail.com' # Email de Quem está enviando o email
    msg['To'] = 'gustavosymoons@gmail.com' # Email Para quem esté sendo enviado o email --> "Recebedor" do email
    password = 'agqgxkvjelcwvgky' # Senha do titular do email/Remetente
    msg.add_header('Content-Type', 'text/html')
    msg.set_payload(corpo_email)

    s = smtplib.SMTP('smtp.gmail.com: 587')
    s.starttls()
    # Credenciais de Login para enviar o email
    s.login(msg['From'], password)
    s.sendmail(msg['From'], [msg['To']], msg.as_string().encode('utf-8'))
    print('Email enviado')


send_email()