import React from 'react';
import { useParams } from 'react-router-dom';

const JobDetailsPage = () => {
  const { id } = useParams();

  return (
    <div className="job-details-page">
      <div className="container">
        <h1>Job Details</h1>
        <p>Job ID: {id}</p>
        <p>Job details functionality coming soon!</p>
      </div>
    </div>
  );
};

export default JobDetailsPage;
