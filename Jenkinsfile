pipeline {
    agent any
    
    environment {
        DOCKER_REGISTRY = 'shristi'
        MODEL_BUCKET = 'your-model-bucket'
        DATA_BUCKET = 'your-data-bucket'
    }
    
    triggers {
        // Retrain weekly
        cron('0 2 * * 0')
        // Trigger on data changes
        upstream(upstreamProjects: 'data-pipeline', threshold: hudson.model.Result.SUCCESS)
    }
    
    stages {
        stage('Data Validation') {
            steps {
                script {
                    docker.image("${DOCKER_REGISTRY}/ml-training:latest").inside {
                        sh '''
                            python scripts/validate_data.py \
                                --data-path ${DATA_BUCKET}/latest \
                                --schema-path config/data_schema.json
                        '''
                    }
                }
            }
        }
        
        stage('Model Training') {
            steps {
                script {
                    docker.image("${DOCKER_REGISTRY}/ml-training:latest").inside {
                        sh '''
                            python scripts/train_model.py \
                                --data-path ${DATA_BUCKET}/latest \
                                --output-path models/new_model \
                                --config config/training_config.yaml
                        '''
                    }
                }
            }
        }
        
        stage('Model Validation') {
            steps {
                script {
                    docker.image("${DOCKER_REGISTRY}/ml-training:latest").inside {
                        sh '''
                            python scripts/validate_model.py \
                                --model-path models/new_model \
                                --test-data ${DATA_BUCKET}/test \
                                --baseline-metrics models/current/metrics.json
                        '''
                    }
                }
            }
        }
        
        stage('A/B Testing Setup') {
            when {
                expression { 
                    return env.MODEL_VALIDATION_PASSED == 'true' 
                }
            }
            steps {
                script {
                    // Deploy to staging for A/B testing
                    sh '''
                        docker build -t ${DOCKER_REGISTRY}/ml-api:staging-${BUILD_NUMBER} \
                            --build-arg MODEL_PATH=models/new_model .
                        docker push ${DOCKER_REGISTRY}/ml-api:staging-${BUILD_NUMBER}
                    '''
                    
                    // Update staging deployment
                    sh '''
                        kubectl set image deployment/ml-api-staging \
                            ml-api=${DOCKER_REGISTRY}/ml-api:staging-${BUILD_NUMBER} \
                            --namespace=staging
                    '''
                }
            }
        }
        
        stage('Production Deployment') {
            when {
                expression { 
                    return env.AB_TEST_PASSED == 'true' 
                }
            }
            steps {
                script {
                    // Blue-green deployment
                    sh '''
                        # Build production image
                        docker build -t ${DOCKER_REGISTRY}/ml-api:prod-${BUILD_NUMBER} \
                            --build-arg MODEL_PATH=models/new_model .
                        docker push ${DOCKER_REGISTRY}/ml-api:prod-${BUILD_NUMBER}
                        
                        # Update blue environment
                        kubectl set image deployment/ml-api-blue \
                            ml-api=${DOCKER_REGISTRY}/ml-api:prod-${BUILD_NUMBER} \
                            --namespace=production
                        
                        # Health check
                        kubectl rollout status deployment/ml-api-blue --namespace=production
                        
                        # Switch traffic
                        kubectl patch service ml-api-service \
                            -p '{"spec":{"selector":{"version":"blue"}}}' \
                            --namespace=production
                    '''
                }
            }
        }
    }
    
    post {
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
