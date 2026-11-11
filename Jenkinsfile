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
  }
}
