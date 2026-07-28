# 🚀 DATUMAGRO - Plataforma Pecuária Inteligente

[![Status](https://img.shields.io/badge/Status-90%25%20Pronto-brightgreen)](README.md)
[![Django](https://img.shields.io/badge/Django-5.x-092E20)](https://djangoproject.com)
[![Flutter](https://img.shields.io/badge/Flutter-MVP-orange)](https://flutter.dev)
[![Tests](https://img.shields.io/badge/Tests-8.57%25-red)](SUMARIO_TESTES.md)

## 🟢 STATUS ATUAL (Dez/2025)

| Componente | Status | Ação Necessária |
|------------|--------|-----------------|
| Backend | 🟢 100% Código | `python manage.py runserver` |
| API | 🟢 Swagger OK | http://localhost:8000/api/swagger/ |
| Flutter | 🟡 MVP | `flutter pub run build_runner build` |
| Testes | 🔴 8.57% | Corrigir modelo Cliente |
| Deploy | 🟢 Render | `bash deploy_render.sh` |

## 🎯 COMO RODAR (2 min)

### Backend
```bash
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

### Flutter
```bash
cd mobile_flutter
flutter pub get
flutter pub run build_runner build
flutter run
```

## 📊 PRÓXIMOS PASSOS (Prioridade)

1. 🔴 **Corrigir Testes** (Cliente refatorado)
2. 🟢 **Rodar Server** (`manage.py runserver`)
3. 🟡 **Build Flutter** (build_runner)
4. 🟢 **Deploy Render** (15 min)
5. 🟢 **Testar Sync** (Flutter ↔ Backend)

## 📚 Documentos Importantes
- [STATUS_100_PERCENTUAL.md](STATUS_100_PERCENTUAL.md)
- [RESUMO_BACKEND_COMPLETO.md](RESUMO_BACKEND_COMPLETO.md)
- [SUMARIO_TESTES.md](SUMARIO_TESTES.md)
- [GUIA_DEPLOY_RENDER.md](GUIA_DEPLOY_RENDER.md)

**Contato:** suporte@datumagro.com
