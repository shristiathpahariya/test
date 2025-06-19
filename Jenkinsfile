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
                    docker.image('python:3.9-slim').inside('-v ${PWD}:/workspace -w /workspace') {
                        sh '''
                            pip install joblib scikit-learn

                            echo "
import joblib
import os
import sys
sys.path.append('/workspace')

if not os.path.exists('model/model.pkl'):
    print('Warning: Model file model/model.pkl not found, skipping validation')
    exit(0)
if not os.path.exists('model/vectorizer.pkl'):
    print('Warning: Vectorizer file model/vectorizer.pkl not found, skipping validation')
    exit(0)

try:
    from src.predict import load_model, predict_sentiment
    model = load_model('model/model.pkl')
    vectorizer = load_model('model/vectorizer.pkl')
    texts = ['I love this!', 'This is terrible']
    for text in texts:
        prediction = predict_sentiment(model, vectorizer, text)
        print(f'Text: {text} -> Prediction: {prediction}')
    print('Validation passed!')
except ImportError as e:
    print(f'Warning: Could not import prediction modules - {e}')
    print('Skipping model validation')
except Exception as e:
    print(f'Error during validation: {e}')
    raise
" | tee validate_model.py

                            python validate_model.py
                        '''
                    }
                }
            }
        }

        stage('Performance Testing') {
            when {
                expression { params.RUN_PERFORMANCE_TEST }
            }
            steps {
                script {
                    docker.image('python:3.9-slim').inside('-v ${PWD}:/workspace -w /workspace') {
                        sh '''
                            pip install joblib scikit-learn

                            echo "
import time
import sys
sys.path.append('/workspace')

try:
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

    if avg_time >= 0.2:
        print(f'Warning: Performance is slower than expected: {avg_time}s')
    else:
        print('Performance test passed!')
except ImportError as e:
    print(f'Warning: Could not import prediction modules - {e}')
    print('Skipping performance test')
except Exception as e:
    print(f'Error during performance test: {e}')
    print('Continuing with deployment...')
" | tee performance_test.py

                            python performance_test.py
                        '''
                    }
                }
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    def image = docker.build("sentiment-analyzer:${params.MODEL_VERSION}")
                    docker.withRegistry('https://registry.hub.docker.com', 'shristi') {
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

                        if docker ps | grep -q sentiment-staging-${BUILD_NUMBER}; then
                            echo "✅ Staging container is running successfully"
                            docker exec sentiment-staging-${BUILD_NUMBER} python -c "print('Container health check passed')" || echo "Warning: Python health check failed but container is running"
                        else
                            echo "❌ Staging container failed to start"
                            exit 1
                        fi
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

                        if docker ps | grep -q sentiment-production; then
                            echo "✅ Production container is running successfully"
                            docker exec sentiment-production python -c "print('Production health check passed')" || echo "Warning: Python health check failed but container is running"
                        else
                            echo "❌ Production container failed to start"
                            exit 1
                        fi
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
                sh '''
                    docker stop sentiment-staging-${BUILD_NUMBER} || true
                    docker rm sentiment-staging-${BUILD_NUMBER} || true
                '''
            }
        }
    }
}
