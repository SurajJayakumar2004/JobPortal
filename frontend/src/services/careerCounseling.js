/**
 * Career Counseling Service
 * Provides comprehensive career analysis and recommendations for job seekers
 */

class CareerCounselingService {
  /**
   * Generate comprehensive career counseling feedback based on skills and job matches
   * @param {Object} analysisData - Resume analysis data containing skills
   * @param {Array} matchResults - Array of job matches with percentages
   * @returns {Object} Comprehensive career counseling feedback
   */
  generateCareerCounselingFeedback(analysisData, matchResults) {
    const skills = analysisData.skills || [];
    const skillCount = skills.length;
    
    // Analyze skill categories
    const techSkills = skills.filter(skill => 
      ['JavaScript', 'Python', 'React', 'Node.js', 'Java', 'C++', 'HTML', 'CSS', 'SQL', 'Git', 'Docker', 'AWS', 'TypeScript', 'MongoDB', 'PostgreSQL', 'Redis', 'Kubernetes', 'Jenkins', 'GraphQL', 'Vue.js', 'Angular', 'Django', 'Flask', 'Spring Boot', 'Laravel', 'PHP', 'Ruby', 'Go', 'Rust', 'Swift', 'Kotlin', 'Flutter', 'React Native', 'Unity', 'TensorFlow', 'PyTorch', 'Pandas', 'NumPy', 'Scikit-learn', 'Machine Learning', 'Data Science', 'Artificial Intelligence'].some(tech => 
        skill.toLowerCase().includes(tech.toLowerCase()) || tech.toLowerCase().includes(skill.toLowerCase())
      )
    );
    
    const softSkills = skills.filter(skill => 
      ['Leadership', 'Communication', 'Teamwork', 'Problem Solving', 'Project Management', 'Time Management', 'Critical Thinking', 'Creativity', 'Adaptability', 'Negotiation', 'Public Speaking', 'Mentoring', 'Strategic Planning', 'Decision Making', 'Conflict Resolution'].some(soft => 
        skill.toLowerCase().includes(soft.toLowerCase()) || soft.toLowerCase().includes(skill.toLowerCase())
      )
    );
    
    const frameworks = skills.filter(skill => 
      ['React', 'Angular', 'Vue.js', 'Django', 'Flask', 'Express.js', 'Spring', 'Laravel', 'Next.js', 'Nuxt.js', 'Svelte', 'Ember.js', 'Bootstrap', 'Tailwind CSS', 'Material-UI', 'Ant Design'].some(framework => 
        skill.toLowerCase().includes(framework.toLowerCase()) || framework.toLowerCase().includes(skill.toLowerCase())
      )
    );
    
    const cloudSkills = skills.filter(skill => 
      ['AWS', 'Azure', 'Google Cloud', 'Docker', 'Kubernetes', 'Terraform', 'CloudFormation', 'Serverless', 'Lambda', 'EC2', 'S3', 'RDS', 'DevOps', 'CI/CD', 'Jenkins', 'GitLab CI', 'GitHub Actions'].some(cloud => 
        skill.toLowerCase().includes(cloud.toLowerCase()) || cloud.toLowerCase().includes(skill.toLowerCase())
      )
    );

    const dataSkills = skills.filter(skill => 
      ['Data Analysis', 'Data Science', 'Machine Learning', 'SQL', 'Python', 'R', 'Tableau', 'Power BI', 'Excel', 'Statistics', 'Big Data', 'Hadoop', 'Spark', 'ETL', 'Data Visualization', 'Business Intelligence'].some(data => 
        skill.toLowerCase().includes(data.toLowerCase()) || data.toLowerCase().includes(skill.toLowerCase())
      )
    );

    // Generate insights
    const insights = [];
    const recommendations = [];
    const careerPaths = [];
    
    // Skill diversity analysis
    if (skillCount >= 20) {
      insights.push("🎯 Exceptional skill diversity - You have a comprehensive and versatile professional toolkit");
    } else if (skillCount >= 15) {
      insights.push("🎯 Strong skill diversity - You have a comprehensive technical toolkit");
    } else if (skillCount >= 10) {
      insights.push("📚 Good skill foundation - Consider expanding into emerging technologies");
    } else if (skillCount >= 5) {
      insights.push("🚀 Growing skill set - Focus on building depth in core technologies");
    } else {
      insights.push("🌱 Developing skill set - Great start! Focus on mastering fundamentals");
    }

    // Technical depth analysis
    if (techSkills.length >= 12) {
      insights.push("💻 Outstanding technical expertise across multiple domains");
      careerPaths.push("Senior Developer", "Technical Lead", "Solutions Architect", "CTO", "Principal Engineer");
    } else if (techSkills.length >= 8) {
      insights.push("💻 Excellent technical depth across multiple domains");
      careerPaths.push("Senior Developer", "Technical Lead", "Solutions Architect");
    } else if (techSkills.length >= 5) {
      insights.push("⚡ Solid technical foundation with room for specialization");
      careerPaths.push("Mid-Level Developer", "Full Stack Developer", "Software Engineer");
    } else if (techSkills.length >= 2) {
      insights.push("🌱 Developing technical skills - Focus on mastering fundamentals");
      careerPaths.push("Junior Developer", "Entry-Level Engineer", "Software Developer");
    } else {
      insights.push("🎯 Consider developing technical skills for technology roles");
    }

    // Leadership potential
    if (softSkills.length >= 5) {
      insights.push("👥 Exceptional leadership potential with strong soft skills");
      recommendations.push("Consider senior leadership or executive roles");
      careerPaths.push("Engineering Manager", "Director of Engineering", "VP of Technology", "Product Manager");
    } else if (softSkills.length >= 3) {
      insights.push("👥 Strong leadership potential with soft skills");
      recommendations.push("Consider team lead or management roles");
      careerPaths.push("Team Lead", "Engineering Manager", "Scrum Master");
    } else if (softSkills.length >= 1) {
      insights.push("🤝 Good interpersonal skills foundation");
      recommendations.push("Develop more soft skills for leadership opportunities");
    }

    // Framework expertise
    if (frameworks.length >= 4) {
      insights.push("🏗️ Exceptional framework versatility shows high adaptability");
      recommendations.push("Leverage diverse framework knowledge for architecture roles");
      careerPaths.push("Frontend Architect", "Full Stack Architect");
    } else if (frameworks.length >= 3) {
      insights.push("🏗️ Strong framework versatility shows adaptability");
      recommendations.push("Leverage framework knowledge for full-stack roles");
    } else if (frameworks.length >= 1) {
      insights.push("📚 Good framework foundation");
      recommendations.push("Consider learning complementary frameworks");
    } else {
      recommendations.push("Learn popular frameworks to increase marketability");
    }

    // Cloud readiness
    if (cloudSkills.length >= 4) {
      insights.push("☁️ Expert-level cloud skills align perfectly with industry trends");
      careerPaths.push("Cloud Architect", "DevOps Engineer", "Site Reliability Engineer", "Platform Engineer");
    } else if (cloudSkills.length >= 2) {
      insights.push("☁️ Cloud-ready profile aligns with industry trends");
      careerPaths.push("Cloud Engineer", "DevOps Engineer");
    } else if (cloudSkills.length >= 1) {
      insights.push("☁️ Good start with cloud technologies");
      recommendations.push("Expand cloud skills - high demand in current market");
    } else {
      recommendations.push("Develop cloud skills - high demand in current market");
    }

    // Data skills analysis
    if (dataSkills.length >= 4) {
      insights.push("📊 Strong data science and analytics capabilities");
      careerPaths.push("Data Scientist", "Data Engineer", "Business Analyst", "Data Architect");
    } else if (dataSkills.length >= 2) {
      insights.push("📈 Good foundation in data-related skills");
      careerPaths.push("Data Analyst", "Business Intelligence Developer");
    }

    // Market alignment analysis
    const avgMatchScore = matchResults.length > 0 
      ? Math.round(matchResults.reduce((sum, job) => sum + job.matchPercentage, 0) / matchResults.length)
      : 0;

    if (avgMatchScore >= 85) {
      insights.push("🎯 Outstanding market alignment - Your skills perfectly match current job demands");
    } else if (avgMatchScore >= 70) {
      insights.push("🎯 Excellent market alignment - Your skills match current job demands");
    } else if (avgMatchScore >= 55) {
      insights.push("📈 Good market fit with opportunities for improvement");
    } else if (avgMatchScore >= 30) {
      insights.push("💡 Moderate skill alignment - Focus on high-demand technologies");
    } else {
      insights.push("💡 Skill gap identified - Focus on in-demand technologies");
    }

    // Specific recommendations based on skill gaps
    const allJobSkills = matchResults.flatMap(job => job.missingSkills || []);
    const skillGaps = {};
    allJobSkills.forEach(skill => {
      skillGaps[skill] = (skillGaps[skill] || 0) + 1;
    });

    const topGaps = Object.entries(skillGaps)
      .sort(([,a], [,b]) => b - a)
      .slice(0, 8)
      .map(([skill]) => skill);

    if (topGaps.length > 0) {
      recommendations.push(`Priority skills to learn: ${topGaps.slice(0, 5).join(', ')}`);
    }

    // Career progression advice
    if (matchResults.some(job => job.experience_level === 'senior' && job.matchPercentage >= 70)) {
      recommendations.push("Ready for senior-level positions in your domain");
    } else if (matchResults.some(job => job.experience_level === 'mid' && job.matchPercentage >= 75)) {
      recommendations.push("Strong candidate for mid-level roles, focus on leadership skills for advancement");
    } else if (matchResults.some(job => job.experience_level === 'entry' && job.matchPercentage >= 60)) {
      recommendations.push("Good fit for entry-level positions, continue building technical depth");
    }

    // Industry-specific recommendations
    if (techSkills.length >= 5 && cloudSkills.length >= 2) {
      recommendations.push("Consider specializing in cloud-native development or DevOps");
    }
    
    if (dataSkills.length >= 3 && techSkills.length >= 3) {
      recommendations.push("Strong profile for data engineering or machine learning roles");
    }

    if (frameworks.length >= 2 && techSkills.length >= 4) {
      recommendations.push("Well-positioned for full-stack development roles");
    }

    // Experience level assessment
    let experienceLevel = 'entry';
    if (skillCount >= 15 && techSkills.length >= 8) {
      experienceLevel = 'senior';
    } else if (skillCount >= 10 && techSkills.length >= 5) {
      experienceLevel = 'mid';
    }

    return {
      insights,
      recommendations,
      careerPaths: [...new Set(careerPaths)].slice(0, 8), // Remove duplicates and limit
      skillBreakdown: {
        technical: techSkills.length,
        soft: softSkills.length,
        frameworks: frameworks.length,
        cloud: cloudSkills.length,
        data: dataSkills.length,
        total: skillCount
      },
      marketAlignment: avgMatchScore,
      topSkillGaps: topGaps.slice(0, 5),
      experienceLevel,
      readinessScore: this.calculateReadinessScore(skillCount, avgMatchScore, techSkills.length, softSkills.length)
    };
  }

  /**
   * Calculate overall career readiness score
   * @param {number} skillCount - Total number of skills
   * @param {number} marketAlignment - Market alignment percentage
   * @param {number} techSkillCount - Number of technical skills
   * @param {number} softSkillCount - Number of soft skills
   * @returns {number} Readiness score (0-100)
   */
  calculateReadinessScore(skillCount, marketAlignment, techSkillCount, softSkillCount) {
    const skillScore = Math.min(skillCount * 4, 40); // Max 40 points for skills
    const marketScore = Math.min(marketAlignment * 0.3, 30); // Max 30 points for market alignment
    const techScore = Math.min(techSkillCount * 2, 20); // Max 20 points for technical skills
    const softScore = Math.min(softSkillCount * 2, 10); // Max 10 points for soft skills
    
    return Math.round(skillScore + marketScore + techScore + softScore);
  }

  /**
   * Get personalized learning recommendations based on skill gaps
   * @param {Array} topSkillGaps - Most in-demand missing skills
   * @param {Object} skillBreakdown - Current skill breakdown
   * @returns {Array} Learning recommendations
   */
  getLearningRecommendations(topSkillGaps, skillBreakdown) {
    const recommendations = [];
    
    if (topSkillGaps.length > 0) {
      recommendations.push({
        type: 'skill',
        title: 'High-Priority Skills',
        items: topSkillGaps.slice(0, 3),
        urgency: 'high'
      });
    }

    if (skillBreakdown.cloud < 2) {
      recommendations.push({
        type: 'category',
        title: 'Cloud Technologies',
        items: ['AWS', 'Docker', 'Kubernetes'],
        urgency: 'medium'
      });
    }

    if (skillBreakdown.frameworks < 2) {
      recommendations.push({
        type: 'category',
        title: 'Modern Frameworks',
        items: ['React', 'Node.js', 'Express.js'],
        urgency: 'medium'
      });
    }

    if (skillBreakdown.soft < 3) {
      recommendations.push({
        type: 'category',
        title: 'Soft Skills',
        items: ['Leadership', 'Communication', 'Project Management'],
        urgency: 'low'
      });
    }

    return recommendations;
  }
}

export default new CareerCounselingService();
