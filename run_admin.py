#!/usr/bin/env python
"""
Скрипт для запуска админ-панели
"""
import uvicorn
from admin import create_admin_app
from config import config

if __name__ == '__main__':
    print("=" * 60)
    print("🔧 Запуск админ-панели SQLAdmin")
    print("=" * 60)
    print(f"\n📍 Главная: http://localhost:{config.ADMIN_PORT}")
    print(f"🔐 Админка: http://localhost:{config.ADMIN_PORT}/admin")
    print("\n📱 Нажмите Ctrl+C для остановки\n")
    print("=" * 60)
    
    app = create_admin_app()
    uvicorn.run(
        app,
        host='0.0.0.0',
        port=config.ADMIN_PORT
    )
