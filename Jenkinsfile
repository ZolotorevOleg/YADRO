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
    }

    options {
        gitLabConnection('education-git.yadro.com')
    }


    stages {
        stage('Quality') {
            parallel {
                stage('Lint') {
                    agent { label 'staging' }
                    steps {
                        script {
                            runLint(env.HADOLINT_IMAGE)
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
                            runSast()
                        }
                    }
                    post {
                        always {
                            archiveArtifacts artifacts: 'reports/bandit.json,reports/bandit.txt', allowEmptyArchive: true
                        }
                    }
                    sh 'docker-compose build'
                }
            }
        }


        stage('Test') {
            agent { label 'staging' }
            when {
                anyOf {
                    branch 'o.zolotorev1/currency-service'
                    branch 'main'
                    changeRequest()
                    tag pattern: "v.*", comparator: "REGEXP"
                }
            }
            steps {
                gitlabCommitStatus('test') {
                    script {
                        runTest()
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
            agent { label 'staging' }
            when {
                anyOf {
                    branch 'main'
                    changeRequest()
                    tag pattern: "v.*", comparator: "REGEXP"
                }
            }
            steps {
                gitlabCommitStatus('build') {
                    script {
                        buildImage()
                    }
                }
            }
        }



        stage('Push to DockerHub') {
            agent { label 'production' }
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
                    pushImage(env.IMAGE_NAME, env.TAG_NAME ?: env.BUILD_NUMBER)
                }
            }
        }


        stage('Deploy') {
            parallel {
                stage('Deploy staging') {
                agent { label 'staging' }
                    when {
                        branch 'main'
                    }
                    steps {
                        build job: 'deploy-job',
                            parameters: [
                                string(name: 'IMAGE_TAG', value: env.BUILD_NUMBER),
                                string(name: 'ENVIRONMENT', value: 'staging')
                            ]
                    }
                }


                stage('Deploy production') {
                agent { label 'production' }
                    when {
                        tag pattern: "v.*", comparator: "REGEXP"
                    }
                    steps {
                        build job: 'deploy-job',
                            parameters: [
                                string(name: 'IMAGE_TAG', value: env.TAG_NAME),
                                string(name: 'ENVIRONMENT', value: 'production')
                            ]
                    }
                }
            }
        }


        stage('Smoke Test'){
            parallel{
                stage('Smoke test staging') {
                    agent { label 'staging' }
                    when {
                        branch 'main'
                    }
                    steps {
                        sh 'curl -f http://localhost:8000/info'
                    }
                }


                stage('Smoke test production') {
                    agent { label 'production' }
                    when {
                        tag pattern: "v.*", comparator: "REGEXP"
                    }
                    steps {
                        sh 'curl -f http://localhost:8000/info'
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


        stage('Security') {
            when {
                branch 'main'
            }
            parallel {
                stage('Pre-commit secrets') {
                    agent { label 'staging' }
                    steps {
                        script {
                            runPrecommit()
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