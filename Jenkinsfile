pipeline {
    agent any
    
    environment {
        DOCKER_REGISTRY = credentials('docker-registry')
        MODEL_BUCKET = 's3://your-model-bucket'
        SLACK_CHANNEL = '#ml-alerts'
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
                        import joblib
                        import os
                        from src.predict import load_model, predict_sentiment
                        
                        # Validate model files exist
                        assert os.path.exists('model/model.pkl'), 'Model file missing'
                        assert os.path.exists('model/vectorizer.pkl'), 'Vectorizer file missing'
                        
                        # Load and test model
                        model = load_model('model/model.pkl')
                        vectorizer = load_model('model/vectorizer.pkl')
                        
                        # Quick prediction test
                        test_texts = ['I love this!', 'This is terrible']
                        for text in test_texts:
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
                params.RUN_PERFORMANCE_TEST == true
            }
            steps {
                script {
                    sh '''
                        python -c "
                        import time
                        from src.predict import predict_sentiment, load_model
                        
                        # Load models
                        model = load_model('model/model.pkl')
                        vectorizer = load_model('model/vectorizer.pkl')
                        
                        # Performance test
                        test_texts = ['Great product!'] * 50  # Reduced for CI/CD speed
                        
                        start_time = time.time()
                        for text in test_texts:
                            predict_sentiment(model, vectorizer, text)
                        end_time = time.time()
                        
                        avg_time = (end_time - start_time) / len(test_texts)
                        print(f'Average prediction time: {avg_time:.4f}s')
                        
                        # Assert performance threshold
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
                params.ENVIRONMENT == 'staging'
            }
            steps {
                script {
                    sh '''
                        # Deploy to staging environment
                        docker run -d --name sentiment-staging-${BUILD_NUMBER} \
                            -p 8001:8000 \
                            sentiment-analyzer:${MODEL_VERSION}
                        
                        # Wait for service to be ready
                        sleep 10
                        
                        # Basic health check
                        docker exec sentiment-staging-${BUILD_NUMBER} \
                            python -c "from src.predict import predict_sentiment; print('Health check:', predict_sentiment('test'))"
                    '''
                }
            }
        }
        
        stage('Deploy to Production') {
            when {
                params.ENVIRONMENT == 'production'
            }
            steps {
                script {
                    // Blue-green deployment
                    sh '''
                        # Stop old container if exists
                        docker stop sentiment-production || true
                        docker rm sentiment-production || true
                        
                        # Start new container
                        docker run -d --name sentiment-production \
                            --restart unless-stopped \
                            -p 8000:8000 \
                            sentiment-analyzer:${MODEL_VERSION}
                        
                        # Health check
                        sleep 15
                        docker exec sentiment-production \
                            python -c "
                            from src.predict import predict_sentiment, load_model
                            model = load_model('model/model.pkl')
                            vectorizer = load_model('model/vectorizer.pkl')
                            result = predict_sentiment(model, vectorizer, 'Amazing service!')
                            print('Production health check:', result)
                            "
                    '''
                }
            }
        }
    }
    
    post {
        success {
            slackSend(
                channel: env.SLACK_CHANNEL,
                color: 'good',
                message: "✅ Sentiment Model Deployed Successfully\n" +
                        "Environment: ${params.ENVIRONMENT}\n" +
                        "Version: ${params.MODEL_VERSION}\n" +
                        "Build: ${BUILD_NUMBER}"
            )
        }
        failure {
            slackSend(
                channel: env.SLACK_CHANNEL,
                color: 'danger',
                message: "❌ Sentiment Model Deployment Failed\n" +
                        "Environment: ${params.ENVIRONMENT}\n" +
                        "Build: ${BUILD_NUMBER}\n" +
                        "Check: ${BUILD_URL}"
            )
        }
        cleanup {
            // Clean up staging containers
            sh '''
                docker stop sentiment-staging-${BUILD_NUMBER} || true
                docker rm sentiment-staging-${BUILD_NUMBER} || true
            '''
        }
    }
}