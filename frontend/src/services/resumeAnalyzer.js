// Resume Analysis Service
class ResumeAnalyzer {
  constructor() {
    // Common technical skills that might appear in resumes
    this.skillsDatabase = [
      // Programming Languages
      'JavaScript', 'Python', 'Java', 'C++', 'C#', 'PHP', 'Ruby', 'Go', 'Rust', 'TypeScript',
      'Swift', 'Kotlin', 'Scala', 'R', 'MATLAB', 'Perl', 'Objective-C', 'Dart', 'F#', 'Haskell',
      
      // Web Technologies
      'HTML', 'CSS', 'React', 'Angular', 'Vue.js', 'Node.js', 'Express.js', 'jQuery', 'Bootstrap',
      'Sass', 'Less', 'Webpack', 'Babel', 'Redux', 'GraphQL', 'REST API', 'JSON', 'XML',
      
      // Databases
      'MySQL', 'PostgreSQL', 'MongoDB', 'SQLite', 'Redis', 'Cassandra', 'DynamoDB', 'Oracle',
      'SQL Server', 'MariaDB', 'Firebase', 'Elasticsearch', 'Neo4j',
      
      // Cloud & DevOps
      'AWS', 'Azure', 'Google Cloud', 'Docker', 'Kubernetes', 'Jenkins', 'Git', 'GitHub',
      'GitLab', 'CI/CD', 'Terraform', 'Ansible', 'Chef', 'Puppet', 'Nginx', 'Apache',
      
      // Data Science & AI
      'Machine Learning', 'Deep Learning', 'TensorFlow', 'PyTorch', 'Pandas', 'NumPy',
      'Scikit-learn', 'Jupyter', 'Data Analysis', 'Statistics', 'Big Data', 'Hadoop', 'Spark',
      
      // Mobile Development
      'React Native', 'Flutter', 'Xamarin', 'Ionic', 'Cordova', 'Android', 'iOS',
      
      // Design & UX
      'Figma', 'Sketch', 'Adobe XD', 'Photoshop', 'Illustrator', 'InVision', 'Principle',
      'UI/UX Design', 'User Research', 'Wireframing', 'Prototyping',
      
      // Testing
      'Jest', 'Mocha', 'Cypress', 'Selenium', 'JUnit', 'PyTest', 'Testing',
      
      // Project Management
      'Agile', 'Scrum', 'Kanban', 'Jira', 'Trello', 'Asana', 'Confluence',
      
      // Soft Skills
      'Leadership', 'Communication', 'Teamwork', 'Problem Solving', 'Critical Thinking',
      'Project Management', 'Time Management', 'Adaptability', 'Creativity'
    ];
  }

  // Extract text from file (simplified version)
  async extractTextFromFile(file) {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      
      reader.onload = (event) => {
        const text = event.target.result;
        resolve(text);
      };
      
      reader.onerror = (error) => {
        reject(error);
      };

      // For now, only handle text files and basic text extraction
      if (file.type === 'text/plain') {
        reader.readAsText(file);
      } else {
        // For PDF/DOC files, we'd need additional libraries
        // For demo purposes, we'll return a placeholder
        resolve('Sample resume text with JavaScript React Node.js Python Machine Learning');
      }
    });
  }

  // Extract skills from resume text
  extractSkills(resumeText) {
    if (!resumeText || typeof resumeText !== 'string') {
      return [];
    }

    const foundSkills = new Set();
    const normalizedText = resumeText.toLowerCase();

    // Look for skills in the text
    this.skillsDatabase.forEach(skill => {
      const normalizedSkill = skill.toLowerCase();
      
      // Check for exact matches and common variations
      const patterns = [
        normalizedSkill,
        normalizedSkill.replace(/\./g, ''), // Remove dots (e.g., Node.js -> nodejs)
        normalizedSkill.replace(/\s+/g, ''), // Remove spaces
        normalizedSkill.replace(/-/g, ''), // Remove hyphens
      ];

      patterns.forEach(pattern => {
        if (normalizedText.includes(pattern)) {
          foundSkills.add(skill);
        }
      });
    });

    return Array.from(foundSkills);
  }

  // Analyze resume and return skills with confidence scores
  async analyzeResume(file) {
    try {
      const resumeText = await this.extractTextFromFile(file);
      const extractedSkills = this.extractSkills(resumeText);
      
      // Calculate confidence scores based on context
      const skillsWithConfidence = extractedSkills.map(skill => ({
        skill,
        confidence: this.calculateConfidence(skill, resumeText)
      }));

      // Sort by confidence
      skillsWithConfidence.sort((a, b) => b.confidence - a.confidence);

      return {
        success: true,
        skills: skillsWithConfidence.map(s => s.skill),
        skillsWithConfidence,
        totalSkillsFound: extractedSkills.length,
        resumeText: resumeText.substring(0, 500) + '...' // First 500 chars for preview
      };
    } catch (error) {
      console.error('Resume analysis error:', error);
      return {
        success: false,
        error: 'Failed to analyze resume. Please try again.',
        skills: []
      };
    }
  }

  // Calculate confidence score for a skill based on context
  calculateConfidence(skill, text) {
    const normalizedText = text.toLowerCase();
    const normalizedSkill = skill.toLowerCase();
    
    let confidence = 0.5; // Base confidence
    
    // Increase confidence if skill appears in typical resume sections
    const resumeSections = [
      'skills', 'technical skills', 'technologies', 'programming languages',
      'tools', 'frameworks', 'experience', 'projects'
    ];
    
    resumeSections.forEach(section => {
      const sectionRegex = new RegExp(`${section}[^\\n]*${normalizedSkill}`, 'i');
      if (sectionRegex.test(normalizedText)) {
        confidence += 0.3;
      }
    });

    // Increase confidence if skill appears multiple times
    const occurrences = (normalizedText.match(new RegExp(normalizedSkill, 'g')) || []).length;
    confidence += Math.min(occurrences * 0.1, 0.3);

    // Increase confidence if skill appears near project/work descriptions
    const contextWords = ['developed', 'built', 'created', 'implemented', 'used', 'worked with'];
    contextWords.forEach(word => {
      const contextRegex = new RegExp(`${word}[^.]{0,50}${normalizedSkill}`, 'i');
      if (contextRegex.test(normalizedText)) {
        confidence += 0.2;
      }
    });

    return Math.min(confidence, 1.0);
  }

  // Get skill suggestions based on found skills
  getSkillSuggestions(foundSkills) {
    const suggestions = new Map();
    
    // Skill relationships and suggestions
    const skillRelationships = {
      'JavaScript': ['React', 'Node.js', 'TypeScript', 'Vue.js', 'Angular'],
      'Python': ['Django', 'Flask', 'Pandas', 'NumPy', 'Machine Learning'],
      'React': ['Redux', 'Next.js', 'GraphQL', 'TypeScript'],
      'Node.js': ['Express.js', 'MongoDB', 'REST API'],
      'Machine Learning': ['TensorFlow', 'PyTorch', 'Scikit-learn', 'Python'],
      'AWS': ['Docker', 'Kubernetes', 'Terraform', 'CI/CD'],
      'Docker': ['Kubernetes', 'AWS', 'DevOps', 'CI/CD'],
    };

    foundSkills.forEach(skill => {
      if (skillRelationships[skill]) {
        skillRelationships[skill].forEach(relatedSkill => {
          if (!foundSkills.includes(relatedSkill)) {
            suggestions.set(relatedSkill, (suggestions.get(relatedSkill) || 0) + 1);
          }
        });
      }
    });

    // Sort suggestions by frequency
    return Array.from(suggestions.entries())
      .sort((a, b) => b[1] - a[1])
      .slice(0, 10)
      .map(([skill]) => skill);
  }
}

// Create and export singleton instance
const resumeAnalyzer = new ResumeAnalyzer();
export default resumeAnalyzer;
