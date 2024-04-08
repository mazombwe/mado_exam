from django.shortcuts import render
from .models import EncryptedFile
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import os 
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives import hashes

# Create your views here.

def index(request):
    if request.method == 'POST':
        if 'encrypt' in request.POST:
            return encrypt_file(request)
        elif 'decrypt' in request.POST:
            return decrypt_file(request)
    return render(request, 'encryptor/index.html')


def encrypt_file(request):
    if 'file' not in request.FILES:
        return render(request, 'encryptor/index.html', {'error_message': 'No file selected'})

    file = request.FILES['file']
    
    # Générer une clé aléatoire pour AES
    key = os.urandom(32)
    
    # Générer un vecteur d'initialisation aléatoire pour le mode CBC
    iv = os.urandom(16)
    
    # Initialiser l'algorithme AES avec la clé et le mode de chiffrement CBC
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    
    # Chiffrer les données du fichier
    file.seek(0)
    padded_data = pad_data(file.read())
    encrypted_data = encryptor.update(padded_data) + encryptor.finalize()
    
    # Fermer le fichier après lecture
    file.close()
    
    # Enregistrer les données chiffrées dans le système de fichiers
    with open('encrypted_file', 'wb') as encrypted_file:
        encrypted_file.write(encrypted_data)
    
    return render(request, 'encryptor/index.html', {'message': 'File encrypted successfully'})

def pad_data(data):
    # Utiliser le padding PKCS7 pour les données
    padder = padding.PKCS7(128).padder()
    padded_data = padder.update(data)
    padded_data += padder.finalize()
    return padded_data


def decrypt_file(request):
    if 'file_id' not in request.POST:
        return render(request, 'encryptor/index.html', {'error_message': 'No file selected'})
    
    file_id = request.POST['file_id']
    try:
        encrypted_file = EncryptedFile.objects.get(pk=file_id)
    except EncryptedFile.DoesNotExist:
        return render(request, 'encryptor/index.html', {'error_message': 'File not found'})

    key = encrypted_file.key.encode()
    cipher = Fernet(key)
    decrypted_data = cipher.decrypt(encrypted_file.file)
    with open('decrypted_file', 'wb') as decrypted_file:
        decrypted_file.write(decrypted_data)
    
    return render(request, 'encryptor/index.html', {'message': 'File decrypted successfully'})
