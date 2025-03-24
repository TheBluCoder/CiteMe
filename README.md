# CiteMe - Academic Citation Management System

CiteMe is a modern, full-stack application designed to help researchers and academics manage their citations and references efficiently. The system provides intelligent citation suggestions, reference management, and seamless integration with academic databases.

🌐 **Live Demo**: [CiteMe Editor](https://cite-me-wpre.vercel.app/editor)

## 🚀 Features

- **Smart Citation Suggestions**: AI-powered citation recommendations based on your research context
- **Reference Management**: Organize and manage your academic references
- **Multiple Citation Styles**: Support for various citation formats (APA, MLA, Chicago, etc.)
- **Real-time Metrics**: Track citation impact and academic metrics
- **Modern UI**: Responsive and intuitive user interface
- **API Integration**: Seamless integration with academic databases and search engines

## 📁 Project Structure

```
CiteMe/
├── frontend/                 # Vue.js 3 frontend application
│   ├── src/                 # Source code
│   ├── public/              # Static assets
│   ├── e2e/                 # End-to-end tests
│   └── dist/                # Production build
├── backend/
│   ├── mainService/         # Core citation service
│   └── metricsService/      # Analytics and metrics service
├── .github/                 # GitHub workflows and templates
├── docker-compose.yml       # Docker services configuration
└── README.md               # Project documentation
```

## 🏗️ Architecture

The application is built using a microservices architecture with three main components:

1. **Frontend Service**: Vue.js 3 application hosted on Vercel
2. **Main Service**: FastAPI-based backend service handling core citation functionality
3. **Metrics Service**: FastAPI-based service for handling academic metrics and analytics

## 🛠️ Tech Stack

### Frontend
- Vue.js 3
- Vite
- TailwindCSS
- TipTap Editor
- Pinia (State Management)
- Vercel (Hosting)

### Backend
- Python 3.11
- FastAPI
- Pinecone
- Gemini
- Azure hosted LLMs
- LangChain
- Various AI/ML libraries

## 🚀 Getting Started

### Prerequisites

- Docker and Docker Compose (for backend services)
- Node.js 20+ (for local frontend development)
- Python 3.11+ (for local backend development)

### Running with Docker Compose (Recommended for Local Development)

1. Clone the repository:
```bash
git clone https://github.com/yourusername/citeme.git
cd citeme
```

2. Create `.env` files in both service directories:
   - `backend/mainService/.env`
   - `backend/metricsService/.env`

3. Build and run the services using Docker Compose:
```bash
docker-compose up --build
```

The services will be available at:
- Main Service: http://localhost:9020
- Metrics Service: http://localhost:9050

### Running Services Individually

If you need to run services separately:

1. Create the Docker network:
```bash
docker network create cite_me
```

2. Run the Metrics Service:
```bash
cd backend/metricsService
docker build -t metrics_service .
docker run -p 9050:8000 \
  --name ms \
  --network cite_me \
  --env-file .env \
  metrics_service
```

3. Run the Main Service:
```bash
cd backend/mainService
docker build -t main_service .
docker run -p 9020:8000 \
  --name mbs \
  --network cite_me \
  --env-file .env \
  -e CREDIBILITY_API_URL=http://ms:8000/api/v1/credibility/batch \
  main_service
```

### Local Development Without Docker

#### Frontend
```bash
cd frontend
npm install
npm run dev
```

#### Main Service
```bash
cd backend/mainService
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate
pip install -r requirements.txt
uvicorn app:app --reload --port 9020
```

#### Metrics Service
```bash
cd backend/metricsService
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate
pip install -r requirements.txt
uvicorn src.main:app --reload --port 9050
```

## 📚 API Documentation

Once the services are running, you can access the API documentation at:
- Main Service: http://localhost:9020/docs
- Metrics Service: http://localhost:9050/docs

## 🧪 Testing

### Frontend Tests
```bash
cd frontend
npm run test:unit    # Run unit tests
npm run test:e2e     # Run end-to-end tests
```

### Backend Tests
```bash
cd backend/mainService
pytest

cd ../metricsService
pytest
```

## 📦 Docker Images

The backend services have their own Dockerfiles:

- `backend/mainService/Dockerfile`: Python-based main service
- `backend/metricsService/Dockerfile`: Python-based metrics service

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Thanks to all contributors who have helped shape this project
- Special thanks to the open-source community for the amazing tools and libraries used in this project 