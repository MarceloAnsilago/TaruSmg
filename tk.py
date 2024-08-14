import streamlit as st
import sqlite3

def listar_tokens():
    conn = sqlite3.connect('enquete.db')
    cursor = conn.cursor()
    cursor.execute('SELECT token, usado FROM tokens')
    tokens = cursor.fetchall()
    conn.close()
    return tokens

def main():
    st.title("Visualização de Tokens")
    
    tokens = listar_tokens()
    st.write("Tokens armazenados:")
    
    for token, usado in tokens:
        status = 'Usado' if usado else 'Não Usado'
        st.write(f'Token: {token} - Status: {status}')

if __name__ == "__main__":
    main()
