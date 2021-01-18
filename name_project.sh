read -p 'Project slug (e.g. my_awesome_project): ' PROJECT_SLUG
read -p 'Full project name (e.g. My Awesome Project): ' PROJECT_NAME
cat project_files.txt | xargs sed -i '' -e "s/\$PROJECT_SLUG/$PROJECT_SLUG/g"
cat project_files.txt | xargs sed -i '' -e "s/\$PROJECT_NAME/$PROJECT_NAME/g"
mv django_server/PROJECT_SLUG django_server/$PROJECT_SLUG
mv README_PROJECT.md README.md
rm name_project.sh project_files.txt
