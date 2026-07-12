pipeline {
    agent any
    
    stages {
        stage('Checkout') {
            steps {
                echo 'Checking out code...'
                checkout scm
            }
        }
        
        stage('Install Dependencies') {
            steps {
                echo 'Installing dependencies...'
                sh '''
                    apt-get update -q
                    apt-get install -y -q python3-pip
                    pip3 install -r requirements.txt
                '''
            }
        }
        
        stage('Lint') {
            steps {
                echo 'Checking code quality...'
                sh 'pip3 install flake8 && flake8 producers/ consumers/ analytics/ --max-line-length=100 --ignore=E501'
            }
        }
        
        stage('Test') {
            steps {
                echo 'Running tests...'
                sh 'pip3 install pytest && pytest tests/ -v'
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