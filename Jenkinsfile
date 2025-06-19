pipeline {
    agent any

    environment {
        DOCKER_REGISTRY = credentials('shristi')
        MODEL_BUCKET = 's3://your-model-bucket'
    }

    parameters {
        string(name: 'MODEL_VERSION', defaultValue: 'latest', description: 'Model version to deploy')
        choice(name: 'ENVIRONMENT', choices: ['staging', 'production'], description: 'Deployment environment')
        booleanParam(name: 'RUN_PERFORMANCE_TEST', defaultValue: true, description: 'Run performance tests')
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Install Dependencies') {
            steps {
                sh '''
                    python3 -m venv venv
                    . venv/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements.txt
                '''
            }
        }

        stage('Model Validation') {
            steps {
                sh '''
                    . venv/bin/activate
                    python validate.py
                '''
            }
        }

        stage('Performance Testing') {
            when {
                expression { params.RUN_PERFORMANCE_TEST }
            }
            steps {
                sh '''
                    . venv/bin/activate
                    python -c "import time; from src.predict import load_model, predict_sentiment; model = load_model('model/model.pkl'); vectorizer = load_model('model/vectorizer.pkl'); test_texts = ['Great product!'] * 50; start = time.time(); [predict_sentiment(model, vectorizer, text) for text in test_texts]; end = time.time(); avg = (end - start)/len(test_texts); print(f'Average time: {avg:.4f}s'); assert avg < 0.2, 'Too slow!'"
                '''
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    def image = docker.build("sentiment-analyzer:${params.MODEL_VERSION}")
                    docker.withRegistry('https://registry.hub.docker.com', 'docker-hub-credentials') {
                        image.push("${params.MODEL_VERSION}")
                        image.push("latest")
                    }
                }
            }
        }

        stage('Deploy to Staging') {
            when {
                expression { params.ENVIRONMENT == 'staging' }
            }
            steps {
                sh """
                    docker stop sentiment-staging-${BUILD_NUMBER} || true
                    docker rm sentiment-staging-${BUILD_NUMBER} || true

                    docker run -d --name sentiment-staging-${BUILD_NUMBER} -p 8001:8000 sentiment-analyzer:${params.MODEL_VERSION}
                    sleep 10

                    docker exec sentiment-staging-${BUILD_NUMBER} python3 -c "from src.predict import predict_sentiment, load_model; model = load_model('model/model.pkl'); vectorizer = load_model('model/vectorizer.pkl'); print('Health check:', predict_sentiment(model, vectorizer, 'test'))"
                """
            }
        }

        stage('Deploy to Production') {
            when {
                expression { params.ENVIRONMENT == 'production' }
            }
            steps {
                sh """
                    docker stop sentiment-production || true
                    docker rm sentiment-production || true

                    docker run -d --name sentiment-production --restart unless-stopped -p 8000:8000 sentiment-analyzer:${params.MODEL_VERSION}
                    sleep 15

                    docker exec sentiment-production python3 -c "from src.predict import predict_sentiment, load_model; model = load_model('model/model.pkl'); vectorizer = load_model('model/vectorizer.pkl'); print('Production health check:', predict_sentiment(model, vectorizer, 'Amazing service!'))"
                """
            }
        }
    }

    post {
        success {
            echo "✅ Deployment Successful: Env=${params.ENVIRONMENT}, Version=${params.MODEL_VERSION}, Build=${BUILD_NUMBER}"
        }
        failure {
            echo "❌ Deployment Failed: Env=${params.ENVIRONMENT}, Build=${BUILD_NUMBER}. See ${BUILD_URL}"
        }
        cleanup {
            sh '''
                docker stop sentiment-staging-${BUILD_NUMBER} || true
                docker rm sentiment-staging-${BUILD_NUMBER} || true
            '''
        }
    }
}
