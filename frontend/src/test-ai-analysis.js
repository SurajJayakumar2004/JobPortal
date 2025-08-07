/**
 * Test script to verify AI Resume Analysis functionality
 */

// Mock resume text for testing
const mockResumeText = `
John Doe
Senior Software Engineer

Experience:
• 5+ years developing web applications using JavaScript, React, and Node.js
• Built scalable backend services with Python and Django
• Experienced with cloud platforms including AWS and Docker
• Database design and optimization with PostgreSQL and MongoDB
• Test-driven development with Jest and Cypress
• Agile development methodologies and team leadership

Skills:
JavaScript, React, Node.js, Python, Django, AWS, Docker, PostgreSQL, MongoDB, 
Jest, Cypress, Git, HTML, CSS, TypeScript, Express.js, REST APIs

Education:
Computer Science, Bachelor's Degree
`;

// Mock jobs data (similar to jobs.json)
const mockJobs = [
  {
    _id: '1',
    title: 'Senior Frontend Developer',
    company_name: 'TechCorp',
    location: 'San Francisco, CA',
    required_skills: ['JavaScript', 'React', 'TypeScript', 'CSS', 'HTML'],
    experience_level: 'senior',
    employment_type: 'full-time',
    salary_range: '$120,000 - $150,000'
  },
  {
    _id: '2', 
    title: 'Full Stack Engineer',
    company_name: 'StartupXYZ',
    location: 'Remote',
    required_skills: ['JavaScript', 'React', 'Node.js', 'PostgreSQL', 'AWS'],
    experience_level: 'mid',
    employment_type: 'full-time',
    salary_range: '$100,000 - $130,000'
  },
  {
    _id: '3',
    title: 'Python Developer',
    company_name: 'DataCorp',
    location: 'New York, NY', 
    required_skills: ['Python', 'Django', 'PostgreSQL', 'Machine Learning'],
    experience_level: 'senior',
    employment_type: 'full-time',
    salary_range: '$110,000 - $140,000'
  }
];

// Test skill extraction
function testSkillExtraction() {
  console.log('🔍 Testing Skill Extraction...\n');
  
  // Simulate skill detection logic
  const skillsDatabase = [
    'JavaScript', 'React', 'Node.js', 'Python', 'Django', 'AWS', 'Docker',
    'PostgreSQL', 'MongoDB', 'Jest', 'Cypress', 'TypeScript', 'HTML', 'CSS',
    'Express.js', 'REST API', 'Git', 'Machine Learning'
  ];
  
  const extractedSkills = [];
  const normalizedText = mockResumeText.toLowerCase();
  
  skillsDatabase.forEach(skill => {
    if (normalizedText.includes(skill.toLowerCase())) {
      extractedSkills.push(skill);
    }
  });
  
  console.log('Resume Text Preview:');
  console.log(mockResumeText.substring(0, 200) + '...\n');
  
  console.log(`✅ Extracted ${extractedSkills.length} skills:`);
  console.log(extractedSkills.join(', '));
  console.log('\n');
  
  return extractedSkills;
}

// Test job matching
function testJobMatching(candidateSkills) {
  console.log('🎯 Testing Job Matching...\n');
  
  const matchResults = mockJobs.map(job => {
    const jobSkills = job.required_skills;
    
    const matchingSkills = candidateSkills.filter(candidateSkill =>
      jobSkills.some(jobSkill =>
        candidateSkill.toLowerCase().includes(jobSkill.toLowerCase()) ||
        jobSkill.toLowerCase().includes(candidateSkill.toLowerCase())
      )
    );
    
    const missingSkills = jobSkills.filter(jobSkill =>
      !candidateSkills.some(candidateSkill =>
        candidateSkill.toLowerCase().includes(jobSkill.toLowerCase()) ||
        jobSkill.toLowerCase().includes(candidateSkill.toLowerCase())
      )
    );

    const matchPercentage = jobSkills.length > 0 
      ? Math.round((matchingSkills.length / jobSkills.length) * 100)
      : 0;

    return {
      ...job,
      matchPercentage,
      matchingSkills,
      missingSkills
    };
  }).sort((a, b) => b.matchPercentage - a.matchPercentage);
  
  console.log('Job Matching Results:');
  console.log('===================\n');
  
  matchResults.forEach((job, index) => {
    console.log(`${index + 1}. ${job.title} at ${job.company_name}`);
    console.log(`   Match Score: ${job.matchPercentage}%`);
    console.log(`   Location: ${job.location}`);
    console.log(`   Salary: ${job.salary_range}`);
    console.log(`   ✅ Matching Skills (${job.matchingSkills.length}): ${job.matchingSkills.join(', ')}`);
    if (job.missingSkills.length > 0) {
      console.log(`   📚 Skills to Learn (${job.missingSkills.length}): ${job.missingSkills.join(', ')}`);
    }
    console.log('');
  });
  
  return matchResults;
}

// Test career counseling analysis
function testCareerCounseling(extractedSkills, matchResults) {
  console.log('🎓 Testing Career Counseling Analysis...\n');
  
  const skillCount = extractedSkills.length;
  
  // Analyze skill categories
  const techSkills = extractedSkills.filter(skill => 
    ['JavaScript', 'Python', 'React', 'Node.js', 'Java', 'C++', 'HTML', 'CSS', 'SQL', 'Git', 'Docker', 'AWS'].includes(skill)
  );
  
  const softSkills = extractedSkills.filter(skill => 
    ['Leadership', 'Communication', 'Teamwork', 'Problem Solving', 'Project Management', 'Time Management'].includes(skill)
  );
  
  const frameworks = extractedSkills.filter(skill => 
    ['React', 'Angular', 'Vue.js', 'Django', 'Flask', 'Express.js', 'Spring', 'Laravel'].includes(skill)
  );
  
  const cloudSkills = extractedSkills.filter(skill => 
    ['AWS', 'Azure', 'Google Cloud', 'Docker', 'Kubernetes', 'Terraform'].includes(skill)
  );

  // Generate insights
  const insights = [];
  const recommendations = [];
  const careerPaths = [];
  
  // Skill diversity analysis
  if (skillCount >= 15) {
    insights.push("🎯 Strong skill diversity - You have a comprehensive technical toolkit");
  } else if (skillCount >= 10) {
    insights.push("📚 Good skill foundation - Consider expanding into emerging technologies");
  } else {
    insights.push("🚀 Growing skill set - Focus on building depth in core technologies");
  }

  // Technical depth analysis
  if (techSkills.length >= 8) {
    insights.push("💻 Excellent technical depth across multiple domains");
    careerPaths.push("Senior Developer", "Technical Lead", "Solutions Architect");
  } else if (techSkills.length >= 5) {
    insights.push("⚡ Solid technical foundation with room for specialization");
    careerPaths.push("Mid-Level Developer", "Full Stack Developer");
  } else {
    insights.push("🌱 Developing technical skills - Focus on mastering fundamentals");
    careerPaths.push("Junior Developer", "Entry-Level Engineer");
  }

  // Leadership potential
  if (softSkills.length >= 3) {
    insights.push("👥 Strong leadership potential with soft skills");
    recommendations.push("Consider team lead or management roles");
    careerPaths.push("Team Lead", "Engineering Manager");
  }

  // Framework expertise
  if (frameworks.length >= 3) {
    insights.push("🏗️ Framework versatility shows adaptability");
    recommendations.push("Leverage framework knowledge for full-stack roles");
  } else if (frameworks.length === 0) {
    recommendations.push("Learn popular frameworks to increase marketability");
  }

  // Cloud readiness
  if (cloudSkills.length >= 2) {
    insights.push("☁️ Cloud-ready profile aligns with industry trends");
    careerPaths.push("Cloud Engineer", "DevOps Engineer");
  } else {
    recommendations.push("Develop cloud skills - high demand in current market");
  }

  // Market alignment analysis
  const avgMatchScore = matchResults.length > 0 
    ? Math.round(matchResults.reduce((sum, job) => sum + job.matchPercentage, 0) / matchResults.length)
    : 0;

  if (avgMatchScore >= 80) {
    insights.push("🎯 Excellent market alignment - Your skills match current job demands");
  } else if (avgMatchScore >= 60) {
    insights.push("📈 Good market fit with opportunities for improvement");
  } else {
    insights.push("💡 Skill gap identified - Focus on in-demand technologies");
  }

  const counselingFeedback = {
    insights,
    recommendations,
    careerPaths: [...new Set(careerPaths)], // Remove duplicates
    skillBreakdown: {
      technical: techSkills.length,
      soft: softSkills.length,
      frameworks: frameworks.length,
      cloud: cloudSkills.length,
      total: skillCount
    },
    marketAlignment: avgMatchScore
  };

  console.log('Career Counseling Analysis:');
  console.log('===========================\n');
  
  console.log('📊 Skill Breakdown:');
  console.log(`   Technical Skills: ${counselingFeedback.skillBreakdown.technical}`);
  console.log(`   Soft Skills: ${counselingFeedback.skillBreakdown.soft}`);
  console.log(`   Frameworks: ${counselingFeedback.skillBreakdown.frameworks}`);
  console.log(`   Cloud Skills: ${counselingFeedback.skillBreakdown.cloud}`);
  console.log(`   Total Skills: ${counselingFeedback.skillBreakdown.total}`);
  console.log(`   Market Alignment: ${counselingFeedback.marketAlignment}%\n`);

  console.log('💡 Professional Insights:');
  counselingFeedback.insights.forEach((insight, index) => {
    console.log(`   ${index + 1}. ${insight}`);
  });
  console.log('');

  console.log('🚀 Career Recommendations:');
  counselingFeedback.recommendations.forEach((rec, index) => {
    console.log(`   ${index + 1}. ${rec}`);
  });
  console.log('');

  console.log('🎯 Suggested Career Paths:');
  counselingFeedback.careerPaths.forEach((path, index) => {
    console.log(`   ${index + 1}. ${path}`);
  });
  console.log('');

  return counselingFeedback;
}

// Run the complete test
function runCompleteTest() {
  console.log('🤖 AI Resume Analysis Test\n');
  console.log('===========================\n');
  
  const extractedSkills = testSkillExtraction();
  const matchResults = testJobMatching(extractedSkills);
  const counselingFeedback = testCareerCounseling(extractedSkills, matchResults);
  
  console.log('\n✅ AI Analysis Test Complete!');
  console.log('\nThis demonstrates how the JobPostingManager will:');
  console.log('1. Extract skills from uploaded resumes');
  console.log('2. Match candidate skills against job requirements');
  console.log('3. Provide skill match percentages and gap analysis');
  console.log('4. Generate comprehensive career counseling feedback');
  console.log('5. Suggest career paths and skill development priorities');
  console.log('6. Provide actionable recommendations for career growth');
}

// Run the test
runCompleteTest();
