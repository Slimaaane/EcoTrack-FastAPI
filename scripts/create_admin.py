#!/usr/bin/env python3
"""
Script pour créer un compte administrateur.
Usage: python scripts/create_admin.py
"""
import sys
import os

# Ajouter le répertoire parent au path pour les imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.db.session import SessionLocal
from app.db.models.user import User, UserRole
from app.core.security import get_password_hash
from sqlalchemy.exc import IntegrityError


def create_admin_user():
    """Crée un compte administrateur interactivement."""
    
    db = SessionLocal()
    
    try:
        print("=== Création d'un compte administrateur ===\n")
        
        # Demander les informations
        email = input("Email de l'admin: ").strip()
        if not email:
            print("❌ L'email est obligatoire.")
            return
        
        username = input("Nom d'utilisateur: ").strip()
        if not username:
            print("❌ Le nom d'utilisateur est obligatoire.")
            return
        
        password = input("Mot de passe: ").strip()
        if not password:
            print("❌ Le mot de passe est obligatoire.")
            return
        
        if len(password) < 8:
            print("⚠️  Attention: mot de passe court (moins de 8 caractères).")
            confirm = input("Continuer quand même? (o/N): ").strip().lower()
            if confirm != 'o':
                print("Annulé.")
                return
        
        # Vérifier si l'utilisateur existe déjà
        existing_user = db.query(User).filter(
            (User.email == email) | (User.username == username)
        ).first()
        
        if existing_user:
            print(f"❌ Un utilisateur avec cet email ou nom d'utilisateur existe déjà.")
            return
        
        # Créer l'utilisateur admin
        hashed_password = get_password_hash(password)
        admin_user = User(
            email=email,
            username=username,
            hashed_password=hashed_password,
            role=UserRole.ADMIN,
            is_active=True
        )
        
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
        
        print(f"\n✅ Compte administrateur créé avec succès!")
        print(f"   ID: {admin_user.id}")
        print(f"   Email: {admin_user.email}")
        print(f"   Username: {admin_user.username}")
        print(f"   Rôle: {admin_user.role.value}")
        
    except IntegrityError as e:
        db.rollback()
        print(f"❌ Erreur: {str(e)}")
    except Exception as e:
        db.rollback()
        print(f"❌ Erreur inattendue: {str(e)}")
    finally:
        db.close()


if __name__ == "__main__":
    create_admin_user()
