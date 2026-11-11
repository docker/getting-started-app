pipeline {
  agent any
  environment {
    IMAGE = "todo-app:${BUILD_NUMBER}"
  }
  stages {
    stage('Checkout') {
      steps { checkout scm }
    }
    stage('Install') {
      steps { sh 'yarn install' }
    }
    stage('Test') {
      steps { sh 'yarn test' }
    }
    stage('Docker Build') {
      steps { sh 'docker build -t $IMAGE .' }
    }
    stage('Deploy') {
      steps {
        sh 'docker rm -f todo-app || true'
        sh 'docker run -d --name todo-app -p 3000:3000 $IMAGE'
      }
    }
  }
}