group "default" {
    targets = [ "video-service", "decision-service", "openface-service" ]
}

target "video-service" {
    context = "./video-service"
    dockerfile = "Dockerfile"
}

target "decision-service" {
    context = "./decision-service"
    dockerfile = "Dockerfile"
}

target "openface-service" {
    context = "./openface-service"
    dockerfile = "Dockerfile"
}
