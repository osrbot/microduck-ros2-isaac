cmake_minimum_required(VERSION 3.16)
project(microduck_description)

find_package(ament_cmake REQUIRED)

install(
  DIRECTORY launch meshes rviz urdf
  DESTINATION share/${PROJECT_NAME}
  PATTERN "__pycache__" EXCLUDE
  PATTERN "*.pyc" EXCLUDE
  PATTERN "._*" EXCLUDE
)

install(
  FILES LICENSE NOTICE README.md
  DESTINATION share/${PROJECT_NAME}
)

install(
  PROGRAMS scripts/publish_home_pose.py
  DESTINATION lib/${PROJECT_NAME}
  RENAME publish_home_pose
)

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  ament_lint_auto_find_test_dependencies()
endif()

ament_package()
