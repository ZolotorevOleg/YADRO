@Library('currency-shared-lib') _

@Library('currency-shared-lib') _

pipeline {
    agent none
    agent none

    options {
        gitLabConnection('education-git.yadro.com')
    }

    environment {
        HADOLINT_IMAGE = 'hadolint/hadolint:v2.14.0-alpine@sha256:7aba693c1442eb31c0b015c129697cb3b6cb7da589d85c7562f9deb435a6657c'
        IMAGE_NAME = 'z0leg/currency-service'
        ZAP_IMAGE = 'zaproxy/zap-stable:2.17.0@sha256:47b883dca0d77aeef1dbb9b8ce1f4baddde348ad5852666e553456a9ad936111'
        K6_IMAGE = 'grafana/k6:master@sha256:07118fc44590c989d2c7bf213fb6a03a20356457b723f55f2051895e5bb363ae'
        TRIVY_IMAGE = 'aquasec/trivy:0.69.3@sha256:7228e304ae0f610a1fad937baa463598cadac0c2ac4027cc68f3a8b997115689'
        VENV_PATH = 'venv/bin/activate'
    }

    stages {
        stage('Setup Python') {
            agent { label 'staging' }
            steps {
                runSetupPython(env.VENV_PATH)
            }
        }


        stage('Quality') {
            parallel {
                stage('Lint') {
                    agent { label 'staging' }
                    steps {
                        script {
                            runLint(env.HADOLINT_IMAGE, env.VENV_PATH)
                        }
                    }
                    post {
                        always {
                            archiveArtifacts artifacts: 'reports/*', fingerprint: true, allowEmptyArchive: true
                        }
                    }
                }

                stage('SAST') {
                    agent { label 'staging' }
                    steps {
                        script {
                            runSast(env.VENV_PATH)
                        }
                    }
                    post {
                        always {
                            archiveArtifacts artifacts: 'reports/bandit.json,reports/bandit.txt', allowEmptyArchive: true
                        }
                    }
                }
            }
        }


        stage('Test') {
            agent { label 'staging' }
            steps {
                gitlabCommitStatus('test') {
                    script {
                        runTest(env.VENV_PATH)
                    }
                }
            }
            post {
                always {
                    archiveArtifacts artifacts: 'reports/*', fingerprint: true
                }
            }
        }


        stage('Build') {
            agent none
            when {
                anyOf {
                    branch 'main'
                    changeRequest()
                    tag pattern: "v.*", comparator: "REGEXP"
                }
            }
            steps {
                script {
                    def imageTag
                    def targetEnv

                    if (env.TAG_NAME) {
                        imageTag = env.TAG_NAME
                        targetEnv = 'production'
                    } else {
                        imageTag = 'latest'
                        targetEnv = 'staging'
                    }

                    node(targetEnv) {
                        buildImage(imageTag)
                    }
                }
            }
        }



        stage('Push to DockerHub') {
            agent { label 'staging' }
            when {
                anyOf {
                    branch 'main'
                    tag pattern: "v.*", comparator: "REGEXP"
                anyOf {
                    branch 'main'
                    tag pattern: "v.*", comparator: "REGEXP"
                }
            }
            steps {
                script {
                    def imageTag = env.TAG_NAME ?: 'latest'
                    pushImage(env.IMAGE_NAME, imageTag)
                }
            }
        }


        stage('Deploy') {
            when {
                anyOf {
                    branch 'main'
                    tag pattern: "v.*", comparator: "REGEXP"
                }
            }
            steps {
                script {
                    def imageTag
                    def targetEnv

                    if (env.TAG_NAME) {
                        imageTag = env.TAG_NAME
                        targetEnv = 'production'
                    } else {
                        imageTag = 'latest'
                        targetEnv = 'staging'
                    }

                    build job: 'deploy-job',
                        parameters: [
                            string(name: 'IMAGE_TAG', value: imageTag),
                            string(name: 'ENVIRONMENT', value: targetEnv)
                        ]
                }
            }
        }


        stage('Smoke Test') {
            when {
                anyOf {
                    branch 'main'
                    tag pattern: "v.*", comparator: "REGEXP"
                }
            }
            steps {
                script {
                    if (env.TAG_NAME) {
                        node('production') {
                            sh 'curl -svf http://localhost:8000/info'
                        }
                    } else {
                        node('staging') {
                            sh 'curl -svf http://localhost:8000/info'
                        }
                    }
                }
            }
        }


        stage('Security') {
            when {
                branch 'main'
            }
            parallel {
                stage('Pre-commit secrets') {
                    agent { label 'staging' }
                    steps {
                        script {
                            runPrecommit(env.VENV_PATH)
                        }
                    }
                    post {
                        always {
                            archiveArtifacts artifacts: 'reports/precommit.txt', allowEmptyArchive: true
                        }
                    }
                }

                stage('SCA image') {
                    agent { label 'staging' }
                    steps {
                        script {
                            scanImage("${env.IMAGE_NAME}:${env.BUILD_NUMBER}", env.TRIVY_IMAGE)
                        }
                    }
                    post {
                        always {
                            archiveArtifacts artifacts: 'reports/trivy-image.json', allowEmptyArchive: true
                        }
                    }
                }

                stage('K6') {
                    agent { label 'staging' }
                    steps {
                        script {
                            runK6('http://10.184.0.114:8000', env.K6_IMAGE)
                        }
                    }
                    post {
                        always {
                            archiveArtifacts artifacts: 'reports/k6.txt', allowEmptyArchive: true
                        }
                    }
                }

                stage('DAST ZAP') {
                    agent { label 'staging' }
                    steps {
                        script {
                            runZapBaseline('http://10.184.0.114:8000', env.ZAP_IMAGE)
                        }
                    }
                    post {
                        always {
                            archiveArtifacts artifacts: 'reports/zap-report.json,reports/zap-report.html', allowEmptyArchive: true
                        }
                    }
                }
            }
        }


        stage('Generate changelog') {
            agent { label 'production' }
            when {
                tag pattern: 'v.*', comparator: 'REGEXP'
            }
            steps {
                script {
                    generateChangelog()
                }
            }
            post {
                always {
                    archiveArtifacts artifacts: 'reports/changelog.md', allowEmptyArchive: true
                }
            }
        }
    }
}