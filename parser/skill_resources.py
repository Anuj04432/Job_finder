"""
Mapping of skills to learning resources.
"""
import urllib.parse
import sys
import json

RESOURCE_MAP = {
    # Data Science & Machine Learning
    "python": [
        {"title": "Python Official Tutorial", "url": "https://docs.python.org/3/tutorial/", "platform": "Python Docs"},
        {"title": "Scientific Computing with Python", "url": "https://www.freecodecamp.org/learn/scientific-computing-with-python/", "platform": "freeCodeCamp"},
    ],
    "sql": [
        {"title": "SQL Tutorial", "url": "https://www.w3schools.com/sql/", "platform": "W3Schools"},
        {"title": "Relational Database Course", "url": "https://www.freecodecamp.org/learn/relational-database/", "platform": "freeCodeCamp"},
    ],
    "machine learning": [
        {"title": "Machine Learning Crash Course", "url": "https://developers.google.com/machine-learning/crash-course", "platform": "Google"},
        {"title": "Machine Learning by Stanford", "url": "https://www.coursera.org/specializations/machine-learning-introduction", "platform": "Coursera"},
    ],
    "statistics": [
        {"title": "Statistics and Probability", "url": "https://www.khanacademy.org/math/statistics-probability", "platform": "Khan Academy"},
    ],
    "pandas": [
        {"title": "Pandas Getting Started", "url": "https://pandas.pydata.org/docs/getting_started/index.html", "platform": "Pandas Docs"},
    ],
    "numpy": [
        {"title": "NumPy Quickstart", "url": "https://numpy.org/doc/stable/user/quickstart.html", "platform": "NumPy Docs"},
    ],
    "scikit-learn": [
        {"title": "Scikit-Learn Tutorials", "url": "https://scikit-learn.org/stable/tutorial/index.html", "platform": "Scikit-Learn Docs"},
    ],
    "deep learning": [
        {"title": "Deep Learning Specialization", "url": "https://www.coursera.org/specializations/deep-learning", "platform": "Coursera"},
        {"title": "Fast.ai Practical Deep Learning", "url": "https://course.fast.ai/", "platform": "Fast.ai"},
    ],
    "data visualization": [
        {"title": "Data Visualization Fundamentals", "url": "https://www.coursera.org/search?query=data%20visualization", "platform": "Coursera"},
    ],
    "tensorflow": [
        {"title": "TensorFlow Tutorials", "url": "https://www.tensorflow.org/tutorials", "platform": "TensorFlow Docs"},
    ],
    "pytorch": [
        {"title": "PyTorch Tutorials", "url": "https://pytorch.org/tutorials/", "platform": "PyTorch Docs"},
    ],
    "r": [
        {"title": "R for Data Science", "url": "https://r4ds.had.co.nz/", "platform": "O'Reilly"},
    ],
    "tableau": [
        {"title": "Tableau Training Videos", "url": "https://www.tableau.com/learn/training", "platform": "Tableau"},
    ],
    "power bi": [
        {"title": "Microsoft Power BI Training", "url": "https://learn.microsoft.com/en-us/training/powerplatform/power-bi", "platform": "Microsoft Learn"},
    ],
    
    # Data Analyst Specific
    "excel": [
        {"title": "Excel Video Training", "url": "https://support.microsoft.com/en-us/office/excel-video-training-9bc05390-e94c-46af-a5b3-d7c22f6990bb", "platform": "Microsoft Support"},
    ],
    "reporting": [
        {"title": "Business Reporting Courses", "url": "https://www.coursera.org/search?query=business%20reporting", "platform": "Coursera"},
    ],
    "data cleaning": [
        {"title": "Data Cleaning Courses", "url": "https://www.coursera.org/search?query=data%20cleaning", "platform": "Coursera"},
    ],
    "google sheets": [
        {"title": "Google Sheets Training", "url": "https://support.google.com/a/users/answer/9282959", "platform": "Google Workspace Learning Center"},
    ],
    "dashboarding": [
        {"title": "Dashboard Design", "url": "https://www.coursera.org/search?query=dashboard%20design", "platform": "Coursera"},
    ],
    "a/b testing": [
        {"title": "A/B Testing", "url": "https://www.udacity.com/course/ab-testing--ud257", "platform": "Udacity"},
    ],
    
    # DevOps & Infrastructure
    "docker": [
        {"title": "Docker Getting Started", "url": "https://docs.docker.com/get-started/", "platform": "Docker Docs"},
    ],
    "kubernetes": [
        {"title": "Kubernetes Basics", "url": "https://kubernetes.io/docs/tutorials/kubernetes-basics/", "platform": "Kubernetes Docs"},
    ],
    "mlops": [
        {"title": "Machine Learning Engineering for Production (MLOps)", "url": "https://www.coursera.org/specializations/machine-learning-engineering-for-production-mlops", "platform": "Coursera"},
    ],
    "model deployment": [
        {"title": "Deploying Machine Learning Models", "url": "https://www.coursera.org/search?query=model%20deployment", "platform": "Coursera"},
    ],
    "aws": [
        {"title": "AWS Skill Builder", "url": "https://skillbuilder.aws/", "platform": "AWS"},
    ],
    "gcp": [
        {"title": "Google Cloud Training", "url": "https://cloud.google.com/training", "platform": "Google Cloud"},
    ],
    "azure": [
        {"title": "Azure Training", "url": "https://learn.microsoft.com/en-us/training/azure/", "platform": "Microsoft Learn"},
    ],
    "ci/cd": [
        {"title": "Continuous Integration", "url": "https://www.atlassian.com/continuous-delivery/continuous-integration", "platform": "Atlassian"},
    ],
    "linux": [
        {"title": "Linux Journey", "url": "https://linuxjourney.com/", "platform": "Linux Journey"},
    ],
    "terraform": [
        {"title": "Terraform Tutorials", "url": "https://developer.hashicorp.com/terraform/tutorials", "platform": "HashiCorp"},
    ],
    "jenkins": [
        {"title": "Jenkins Tutorials", "url": "https://www.jenkins.io/doc/tutorials/", "platform": "Jenkins Docs"},
    ],
    "bash": [
        {"title": "Bash Scripting Tutorial", "url": "https://mywiki.wooledge.org/BashGuide", "platform": "Greg's Wiki"},
    ],
    "ansible": [
        {"title": "Ansible Getting Started", "url": "https://docs.ansible.com/ansible/latest/getting_started/index.html", "platform": "Ansible Docs"},
    ],
    "monitoring": [
        {"title": "System Monitoring Courses", "url": "https://www.coursera.org/search?query=system%20monitoring", "platform": "Coursera"},
    ],
    "prometheus": [
        {"title": "Prometheus Getting Started", "url": "https://prometheus.io/docs/prometheus/latest/getting_started/", "platform": "Prometheus Docs"},
    ],
    "grafana": [
        {"title": "Grafana Tutorials", "url": "https://grafana.com/tutorials/", "platform": "Grafana"},
    ],

    # Backend & General Engineering
    "rest api": [
        {"title": "REST API Tutorial", "url": "https://restfulapi.net/", "platform": "REST API Tutorial"},
    ],
    "git": [
        {"title": "Pro Git Book", "url": "https://git-scm.com/book/en/v2", "platform": "Git"},
    ],
    "java": [
        {"title": "Java Tutorial", "url": "https://docs.oracle.com/javase/tutorial/", "platform": "Oracle Docs"},
    ],
    "node.js": [
        {"title": "Node.js Introduction", "url": "https://nodejs.dev/en/learn/", "platform": "Node.js Docs"},
    ],
    "fastapi": [
        {"title": "FastAPI Tutorial", "url": "https://fastapi.tiangolo.com/tutorial/", "platform": "FastAPI Docs"},
    ],
    "flask": [
        {"title": "Flask Tutorial", "url": "https://flask.palletsprojects.com/en/2.3.x/tutorial/", "platform": "Flask Docs"},
    ],
    "django": [
        {"title": "Django Tutorial", "url": "https://docs.djangoproject.com/en/stable/intro/tutorial01/", "platform": "Django Docs"},
    ],
    "postgresql": [
        {"title": "PostgreSQL Tutorial", "url": "https://www.postgresqltutorial.com/", "platform": "PostgreSQL Tutorial"},
    ],
    "mongodb": [
        {"title": "MongoDB University", "url": "https://learn.mongodb.com/", "platform": "MongoDB"},
    ],
    "microservices": [
        {"title": "Microservices Architecture", "url": "https://microservices.io/", "platform": "Microservices.io"},
    ],
    "system design": [
        {"title": "System Design Primer", "url": "https://github.com/donnemartin/system-design-primer", "platform": "GitHub"},
    ],
    "redis": [
        {"title": "Redis University", "url": "https://university.redis.com/", "platform": "Redis"},
    ],
    "data structures": [
        {"title": "Data Structures Course", "url": "https://www.coursera.org/learn/data-structures", "platform": "Coursera"},
    ],
    "algorithms": [
        {"title": "Algorithms Course", "url": "https://www.coursera.org/specializations/algorithms", "platform": "Coursera"},
    ],
    "c++": [
        {"title": "C++ Tutorial", "url": "https://cplusplus.com/doc/tutorial/", "platform": "cplusplus.com"},
    ],
    "testing": [
        {"title": "Software Testing Courses", "url": "https://www.coursera.org/search?query=software%20testing", "platform": "Coursera"},
    ],
    "object-oriented programming": [
        {"title": "Object-Oriented Programming Courses", "url": "https://www.coursera.org/search?query=object%20oriented%20programming", "platform": "Coursera"},
    ],
    
    # Frontend
    "javascript": [
        {"title": "JavaScript Guide", "url": "https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide", "platform": "MDN"},
        {"title": "JavaScript Algorithms and Data Structures", "url": "https://www.freecodecamp.org/learn/javascript-algorithms-and-data-structures/", "platform": "freeCodeCamp"},
    ],
    "react": [
        {"title": "React Official Documentation", "url": "https://react.dev/learn", "platform": "React Docs"},
    ],
    "html": [
        {"title": "HTML Basics", "url": "https://developer.mozilla.org/en-US/docs/Learn/Getting_started_with_the_web/HTML_basics", "platform": "MDN"},
    ],
    "css": [
        {"title": "CSS Basics", "url": "https://developer.mozilla.org/en-US/docs/Learn/Getting_started_with_the_web/CSS_basics", "platform": "MDN"},
    ],
    "typescript": [
        {"title": "TypeScript Handbook", "url": "https://www.typescriptlang.org/docs/handbook/intro.html", "platform": "TypeScript Docs"},
    ],
    "next.js": [
        {"title": "Next.js Foundations", "url": "https://nextjs.org/learn", "platform": "Next.js Docs"},
    ],
    "vue": [
        {"title": "Vue.js Guide", "url": "https://vuejs.org/guide/introduction.html", "platform": "Vue Docs"},
    ],
    "redux": [
        {"title": "Redux Fundamentals", "url": "https://redux.js.org/tutorials/fundamentals/part-1-overview", "platform": "Redux Docs"},
    ],
    "tailwind css": [
        {"title": "Tailwind CSS Documentation", "url": "https://tailwindcss.com/docs/installation", "platform": "Tailwind Docs"},
    ],
    "responsive design": [
        {"title": "Responsive Web Design", "url": "https://www.freecodecamp.org/learn/2022/responsive-web-design/", "platform": "freeCodeCamp"},
    ],
    "webpack": [
        {"title": "Webpack Getting Started", "url": "https://webpack.js.org/guides/getting-started/", "platform": "Webpack Docs"},
    ],
    "express.js": [
        {"title": "Express/Node introduction", "url": "https://developer.mozilla.org/en-US/docs/Learn/Server-side/Express_Nodejs/Introduction", "platform": "MDN"},
    ],
    
    # Design & Product
    "figma": [
        {"title": "Figma Learn", "url": "https://help.figma.com/hc/en-us", "platform": "Figma"},
    ],
    "product strategy": [
        {"title": "Product Strategy Courses", "url": "https://www.coursera.org/search?query=product%20strategy", "platform": "Coursera"},
    ],
    "roadmapping": [
        {"title": "Product Roadmapping Courses", "url": "https://www.coursera.org/search?query=product%20roadmap", "platform": "Coursera"},
    ],
    "stakeholder management": [
        {"title": "Stakeholder Management Courses", "url": "https://www.coursera.org/search?query=stakeholder%20management", "platform": "Coursera"},
    ],
    "agile": [
        {"title": "Agile Crash Course", "url": "https://www.atlassian.com/agile", "platform": "Atlassian"},
    ],
    "user research": [
        {"title": "UX Research Courses", "url": "https://www.coursera.org/search?query=ux%20research", "platform": "Coursera"},
    ],
    "scrum": [
        {"title": "What is Scrum?", "url": "https://www.scrum.org/resources/what-is-scrum", "platform": "Scrum.org"},
    ],
    "data analysis": [
        {"title": "Data Analysis Courses", "url": "https://www.coursera.org/search?query=data%20analysis", "platform": "Coursera"},
    ],
    "wireframing": [
        {"title": "Wireframing Courses", "url": "https://www.coursera.org/search?query=wireframing", "platform": "Coursera"},
    ],
    "jira": [
        {"title": "Jira Tutorials", "url": "https://www.atlassian.com/software/jira/guides", "platform": "Atlassian"},
    ],
    "market research": [
        {"title": "Market Research Courses", "url": "https://www.coursera.org/search?query=market%20research", "platform": "Coursera"},
    ],
    "prototyping": [
        {"title": "Prototyping Courses", "url": "https://www.coursera.org/search?query=prototyping", "platform": "Coursera"},
    ],
    "adobe xd": [
        {"title": "Adobe XD Learn & Support", "url": "https://helpx.adobe.com/xd/tutorials.html", "platform": "Adobe"},
    ],
    "sketch": [
        {"title": "Sketch Documentation", "url": "https://www.sketch.com/docs/", "platform": "Sketch"},
    ],
    "usability testing": [
        {"title": "Usability Testing Courses", "url": "https://www.coursera.org/search?query=usability%20testing", "platform": "Coursera"},
    ],
    "design systems": [
        {"title": "Design Systems Courses", "url": "https://www.coursera.org/search?query=design%20systems", "platform": "Coursera"},
    ],
    "interaction design": [
        {"title": "Interaction Design Courses", "url": "https://www.coursera.org/search?query=interaction%20design", "platform": "Coursera"},
    ],
    "photoshop": [
        {"title": "Photoshop Tutorials", "url": "https://helpx.adobe.com/photoshop/tutorials.html", "platform": "Adobe"},
    ]
}

def get_resources_for_skills(skills: list[str]) -> dict[str, list[dict]]:
    """Returns {skill: [resource, ...]} for each input skill.
    For any skill NOT in RESOURCE_MAP, generate a fallback entry: a
    single resource pointing to a YouTube search URL for that skill
    name (https://www.youtube.com/results?search_query=<skill>+tutorial),
    so every skill always returns at least one usable link, never an
    empty list."""
    result = {}
    for skill in skills:
        if not isinstance(skill, str) or not skill.strip():
            continue
            
        skill_clean = skill.strip().lower()
        if skill_clean in RESOURCE_MAP:
            result[skill_clean] = RESOURCE_MAP[skill_clean]
        else:
            query = urllib.parse.quote_plus(f"{skill_clean} tutorial")
            result[skill_clean] = [
                {
                    "title": f"Learn {skill.strip()}",
                    "url": f"https://www.youtube.com/results?search_query={query}",
                    "platform": "YouTube"
                }
            ]
            
    return result

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python skill_resources.py <comma_separated_skills>")
        sys.exit(1)
        
    skills = [s.strip() for s in sys.argv[1].split(",") if s.strip()]
    result = get_resources_for_skills(skills)
    print(json.dumps(result, indent=2))
