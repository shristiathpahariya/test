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

        stage('Model Validation') {
            steps {
                script {
                    sh '''
                        python -c "
import joblib, os
from src.predict import load_model, predict_sentiment

assert os.path.exists('model/model.pkl'), 'Model file missing'
assert os.path.exists('model/vectorizer.pkl'), 'Vectorizer file missing'

model = load_model('model/model.pkl')
vectorizer = load_model('model/vectorizer.pkl')

texts = ['I love this!', 'This is terrible']
for text in texts:
    prediction = predict_sentiment(model, vectorizer, text)
    print(f'Text: {text} -> Prediction: {prediction}')

print('Validation passed!')
                        "
                    '''
                }
            }
        }

        stage('Performance Testing') {
            when {
                expression { params.RUN_PERFORMANCE_TEST }
            }
            steps {
                script {
                    sh '''
                        python -c "
import time
from src.predict import predict_sentiment, load_model

model = load_model('model/model.pkl')
vectorizer = load_model('model/vectorizer.pkl')

test_texts = ['Great product!'] * 50

start_time = time.time()
for text in test_texts:
    predict_sentiment(model, vectorizer, text)
end_time = time.time()

avg_time = (end_time - start_time) / len(test_texts)
print(f'Average prediction time: {avg_time:.4f}s')

assert avg_time < 0.2, f'Performance too slow: {avg_time}s'
                        "
                    '''
                }
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
                script {
                    sh '''
                        docker run -d --name sentiment-staging-${BUILD_NUMBER} \
                            -p 8001:8000 \
                            sentiment-analyzer:${MODEL_VERSION}

                        sleep 10

                        docker exec sentiment-staging-${BUILD_NUMBER} \
                            python -c "from src.predict import predict_sentiment, load_model; model = load_model('model/model.pkl'); vectorizer = load_model('model/vectorizer.pkl'); print('Health check:', predict_sentiment(model, vectorizer, 'test'))"
                    '''
                }
            }
        }

        stage('Deploy to Production') {
            when {
                expression { params.ENVIRONMENT == 'production' }
            }
            steps {
                script {
                    sh '''
                        docker stop sentiment-production || true
                        docker rm sentiment-production || true

                        docker run -d --name sentiment-production \
                            --restart unless-stopped \
                            -p 8000:8000 \
                            sentiment-analyzer:${MODEL_VERSION}

                        sleep 15

                        docker exec sentiment-production \
                            python -c "from src.predict import predict_sentiment, load_model; model = load_model('model/model.pkl'); vectorizer = load_model('model/vectorizer.pkl'); result = predict_sentiment(model, vectorizer, 'Amazing service!'); print('Production health check:', result)"
                    '''
                }
            }
        }
    }

    post {
        success {
            echo "✅ Sentiment Model Deployment Succeeded - Environment: ${params.ENVIRONMENT}, Build: ${BUILD_NUMBER}"
        }
        failure {
            echo "❌ Sentiment Model Deployment Failed - Environment: ${params.ENVIRONMENT}, Build: ${BUILD_NUMBER}. Check build logs for details."
        }
        cleanup {
            script {
                node {
                    sh '''
                        docker stop sentiment-staging-${BUILD_NUMBER} || true
                        docker rm sentiment-staging-${BUILD_NUMBER} || true
                    '''
                }
            }
        }
    }
}
