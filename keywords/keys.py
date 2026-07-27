job_keywords = {
    "Data Analyst": [
        "SQL", "Python", "Excel", "Power BI", "Tableau",
        "Data Visualization", "Pandas", "NumPy", "Statistics",
        "Data Cleaning", "ETL", "Dashboard", "Business Intelligence",'Business Insights',
        "A/B Testing", "Data Modeling", "Reporting", "Forecasting",'Advanced Excel'
    ],

    "Data Scientist": [
        "Python", "Machine Learning", "Deep Learning", "TensorFlow",
        "PyTorch", "Scikit-learn", "Pandas", "NumPy", "Statistics",
        "Feature Engineering", "Model Deployment", "NLP", "Computer Vision",
        "XGBoost", "Random Forest", "Data Mining", "MLOps"
    ],

    "Machine Learning Engineer": [
        "Python", "Machine Learning", "Scikit-learn", "TensorFlow",
        "PyTorch", "Docker", "Kubernetes", "MLflow", "AWS",
        "Azure", "GCP", "Model Deployment", "REST API",
        "CI/CD", "Feature Engineering", "MLOps"
    ],

    "AI Engineer": [
        "Python", "LLM", "Generative AI", "LangChain",
        "RAG", "OpenAI API", "Prompt Engineering",
        "Vector Database", "Pinecone", "FAISS",
        "Transformers", "Hugging Face", "FastAPI",
        "Docker", "Git", "Python"
    ],

    "Software Engineer": [
        "Java", "Python", "C++", "JavaScript",
        "Git", "REST API", "OOP", "Data Structures",
        "Algorithms", "SQL", "System Design",
        "Debugging", "Unit Testing", "Agile", "CI/CD"
    ],

    "Backend Developer": [
        "Python", "Django", "Flask", "FastAPI",
        "Node.js", "Express.js", "REST API",
        "PostgreSQL", "MySQL", "MongoDB",
        "Docker", "Redis", "JWT", "Git"
    ],

    "Frontend Developer": [
        "HTML", "CSS", "JavaScript", "React",
        "Next.js", "TypeScript", "Redux",
        "Bootstrap", "Tailwind CSS",
        "Responsive Design", "Git"
    ],

    "Full Stack Developer": [
        "React", "Node.js", "Express.js", "MongoDB",
        "JavaScript", "TypeScript", "REST API",
        "Git", "Docker", "SQL", "AWS",
        "HTML", "CSS"
    ],

    "DevOps Engineer": [
        "Docker", "Kubernetes", "Jenkins",
        "GitHub Actions", "Terraform",
        "AWS", "Azure", "Linux",
        "Bash", "CI/CD", "Monitoring",
        "Prometheus", "Grafana"
    ],

    "Cloud Engineer": [
        "AWS", "Azure", "Google Cloud",
        "Docker", "Kubernetes",
        "Terraform", "CloudFormation",
        "Networking", "Linux",
        "Security", "IAM"
    ],

    "Cyber Security Analyst": [
        "SIEM", "SOC", "Firewalls",
        "Penetration Testing", "OWASP",
        "Wireshark", "Nmap", "Splunk",
        "Incident Response", "Network Security",
        "Risk Assessment"
    ],

    "Business Analyst": [
        "Requirements Gathering", "SQL",
        "Excel", "Power BI", "Tableau",
        "Stakeholder Management",
        "Business Process", "Agile",
        "JIRA", "Documentation"
    ],

    "UI/UX Designer": [
        "Figma", "Adobe XD", "Wireframing",
        "Prototyping", "User Research",
        "Design Thinking", "Usability Testing",
        "Interaction Design"
    ],

    "QA Engineer": [
        "Selenium", "Manual Testing",
        "Automation Testing", "JUnit",
        "Test Cases", "Bug Tracking",
        "JIRA", "API Testing",
        "Postman", "Regression Testing"
    ]
}


ROLE_SKILLS = {
    "Data Scientist": {
        "python", "sql", "machine learning", "statistics", "pandas", "numpy",
        "scikit-learn", "deep learning", "data visualization", "tensorflow",
        "pytorch", "data cleaning", "feature engineering", "a/b testing",
        "r", "tableau", "power bi",
    },
    "Data Analyst": {
        "sql", "excel", "python", "power bi", "tableau", "data visualization",
        "data cleaning", "statistics", "reporting", "google sheets",
        "dashboarding", "a/b testing",
    },
    "Machine Learning Engineer": {
        "python", "machine learning", "deep learning", "tensorflow", "pytorch",
        "docker", "kubernetes", "mlops", "model deployment", "aws", "gcp",
        "azure", "sql", "data pipelines", "fastapi", "flask", "git",
    },
    "Backend Developer": {
        "python", "java", "node.js", "sql", "rest api", "fastapi", "flask",
        "django", "docker", "git", "postgresql", "mongodb", "microservices",
        "aws", "system design", "redis",
    },
    "Frontend Developer": {
        "javascript", "typescript", "react", "html", "css", "next.js",
        "vue", "redux", "tailwind css", "git", "responsive design",
        "webpack", "figma",
    },
    "Full Stack Developer": {
        "javascript", "python", "react", "node.js", "sql", "html", "css",
        "rest api", "git", "mongodb", "docker", "typescript", "express.js",
    },
    "DevOps Engineer": {
        "docker", "kubernetes", "aws", "azure", "gcp", "ci/cd", "terraform",
        "jenkins", "linux", "bash", "git", "ansible", "monitoring",
        "prometheus", "grafana",
    },
    "Software Engineer": {
        "python", "java", "c++", "data structures", "algorithms", "git",
        "sql", "system design", "rest api", "docker", "testing",
        "object-oriented programming",
    },
    "Product Manager": {
        "product strategy", "roadmapping", "user research", "agile", "scrum",
        "stakeholder management", "data analysis", "sql", "wireframing",
        "a/b testing", "jira", "market research",
    },
    "UI/UX Designer": {
        "figma", "adobe xd", "sketch", "wireframing", "prototyping",
        "user research", "usability testing", "design systems",
        "interaction design", "photoshop",
    },
}
 
 
# Small synonym map so close variants count as a match
# (e.g. "ML" and "Machine Learning" should be treated the same)
SYNONYMS = {
    "ml": "machine learning",
    "dl": "deep learning",
    "js": "javascript",
    "ts": "typescript",
    "nlp": "natural language processing",
    "cv": "computer vision",
    "k8s": "kubernetes",
    "postgres": "postgresql",
    "reactjs": "react",
    "node": "node.js",
    "oop": "object-oriented programming",
}
 