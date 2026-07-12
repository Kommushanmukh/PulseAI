pipeline {
    agent any
    
    stages {
        stage('Checkout') {
            steps {
                git branch: 'dev',
                    url: 'https://github.com/Kommushanmukh/PulseAI.git'
            }
        }
        
        stage('Install Dependencies') {
            steps {
                sh 'pip3 install -r requirements.txt --break-system-packages'
            }
        }
        
        stage('Test') {
            steps {
                sh 'pip3 install pytest --break-system-packages && pytest tests/ -v'
            }
        }
    }
    
    post {
        success {
            echo '✅ Pipeline passed!'
        }
        failure {
            echo '❌ Pipeline failed!'
        }
    }
}