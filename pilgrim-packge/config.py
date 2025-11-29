import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'postgresql://neondb_owner:npg_uYcyz7nM5Wqh@ep-shy-snow-adyq945n-pooler.c-2.us-east-1.aws.neon.tech/pilgrimpackages?sslmode=require&channel_binding=require')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    CACHE_TYPE = 'simple'
