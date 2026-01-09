-- Script SQL pour créer la base de données Eisenhower TODO
-- À exécuter dans phpMyAdmin ou MySQL Workbench

-- Créer la base de données
CREATE DATABASE IF NOT EXISTS eisenhower_todo 
CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;

-- Sélectionner la base de données
USE eisenhower_todo;

-- Afficher un message de confirmation
SELECT 'Base de données eisenhower_todo créée avec succès!' AS Message;

-- Optionnel : Créer un utilisateur dédié (recommandé pour la production)
-- CREATE USER 'eisenhower_user'@'localhost' IDENTIFIED BY 'votre_mot_de_passe_securise';
-- GRANT ALL PRIVILEGES ON eisenhower_todo.* TO 'eisenhower_user'@'localhost';
-- FLUSH PRIVILEGES;
