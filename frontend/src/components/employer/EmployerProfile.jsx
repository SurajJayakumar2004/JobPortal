/**
 * Employer Profile Management Component
 * Handles company profile creation, editing, and display
 */

import React, { useState, useEffect } from 'react';
import { useToast } from '../Toast';
import { getStatusErrorMessage } from '../../utils/errorHandler';
import { employerProfileAPI, INDUSTRIES, COMPANY_SIZES } from '../../services/employerAPI';

const EmployerProfile = ({ companyProfile, setCompanyProfile }) => {
  const { showSuccess, showError } = useToast();
  const [isEditing, setIsEditing] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    logo: null,
    website: '',
    industry: '',
    size: '',
    location: {
      address: '',
      city: '',
      state: '',
      country: '',
      zipCode: ''
    },
    contact: {
      email: '',
      phone: '',
      linkedIn: '',
      twitter: ''
    },
    culture: {
      values: '',
      benefits: '',
      workEnvironment: '',
      diversity: ''
    },
    founded: '',
    headquarters: ''
  });

  useEffect(() => {
    if (companyProfile) {
      setFormData(companyProfile);
    } else {
      // Load existing profile if available
      loadCompanyProfile();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [companyProfile]);

  const loadCompanyProfile = async () => {
    try {
      setIsLoading(true);
      const response = await employerProfileAPI.getProfile();
      if (response.success && response.data.profile) {
        const profile = response.data.profile;
        setFormData({
          name: profile.company_name || '',
          description: profile.description || '',
          logo: null,
          website: profile.website || '',
          industry: profile.industry || '',
          size: profile.company_size || '',
          location: {
            address: profile.location?.address || '',
            city: profile.location?.city || '',
            state: profile.location?.state || '',
            country: profile.location?.country || '',
            zipCode: profile.location?.postal_code || ''
          },
          contact: {
            email: profile.contact?.email || '',
            phone: profile.contact?.phone || '',
            linkedIn: profile.contact?.linkedin || '',
            twitter: ''
          },
          culture: {
            values: Array.isArray(profile.culture?.values) ? profile.culture.values.join(', ') : '',
            benefits: Array.isArray(profile.culture?.benefits) ? profile.culture.benefits.join(', ') : '',
            workEnvironment: profile.culture?.work_environment || '',
            diversity: ''
          },
          founded: '',
          headquarters: profile.location?.city || ''
        });
        setCompanyProfile(profile);
      }
    } catch (error) {
      console.error('Failed to load company profile:', error);
      showError(getStatusErrorMessage(error.message));
    } finally {
      setIsLoading(false);
    }
  };

  const handleInputChange = (section, field, value) => {
    if (section) {
      setFormData(prev => ({
        ...prev,
        [section]: {
          ...prev[section],
          [field]: value
        }
      }));
    } else {
      setFormData(prev => ({
        ...prev,
        [field]: value
      }));
    }
  };

  const handleLogoUpload = (event) => {
    const file = event.target.files[0];
    if (file) {
      // Validate file type and size
      if (!file.type.startsWith('image/')) {
        showError('Please upload an image file');
        return;
      }
      if (file.size > 5 * 1024 * 1024) { // 5MB limit
        showError('Logo file size must be less than 5MB');
        return;
      }
      
      setFormData(prev => ({ ...prev, logo: file }));
    }
  };

  const handleSave = async () => {
    try {
      setIsLoading(true);
      
      // Validate required fields
      if (!formData.name || !formData.description || !formData.industry) {
        showError('Please fill in all required fields (Company Name, Description, Industry)');
        return;
      }

      // Prepare profile data for API
      const profileData = {
        company_name: formData.name,
        description: formData.description,
        industry: formData.industry,
        company_size: formData.size,
        website: formData.website,
        location: {
          address: formData.location.address,
          city: formData.location.city,
          state: formData.location.state,
          country: formData.location.country,
          postal_code: formData.location.zipCode
        },
        contact: {
          email: formData.contact.email,
          phone: formData.contact.phone,
          linkedin: formData.contact.linkedIn
        },
        culture: {
          values: formData.culture.values ? formData.culture.values.split(',').map(v => v.trim()) : [],
          benefits: formData.culture.benefits ? formData.culture.benefits.split(',').map(b => b.trim()) : [],
          work_environment: formData.culture.workEnvironment
        }
      };

      // Upload logo if a new file was selected
      if (formData.logo && typeof formData.logo === 'object') {
        try {
          const logoResponse = await employerProfileAPI.uploadLogo(formData.logo);
          if (logoResponse.success) {
            profileData.logo_url = logoResponse.data.logo_url;
          }
        } catch (logoError) {
          console.error('Failed to upload logo:', logoError);
          showError('Logo upload failed, but profile will be saved without logo');
        }
      }

      // Save profile data
      const response = await employerProfileAPI.updateProfile(profileData);
      
      if (response.success) {
        setCompanyProfile(response.data.profile);
        setIsEditing(false);
        showSuccess('Company profile updated successfully!');
      }
    } catch (error) {
      const errorMessage = getStatusErrorMessage(error);
      showError(`Failed to update profile: ${errorMessage}`);
    } finally {
      setIsLoading(false);
    }
  };

  const industryOptions = INDUSTRIES;

  const companySizes = COMPANY_SIZES;

  if (isLoading && !formData.name) {
    return (
      <div className="loading-container">
        <div className="loading-spinner"></div>
        <div className="loading-text">Loading company profile...</div>
      </div>
    );
  }

  return (
    <div className="employer-profile">
      <div className="flex justify-between items-center mb-8">
        <div>
          <h2 className="text-3xl font-bold text-gray-900 mb-2">Company Profile</h2>
          <p className="text-gray-600">Manage your company information and showcase your brand</p>
        </div>
        <div className="space-x-3">
          {isEditing ? (
            <>
              <button
                onClick={() => setIsEditing(false)}
                className="btn-modern-secondary"
                disabled={isLoading}
              >
                <span className="mr-2">❌</span>
                Cancel
              </button>
              <button
                onClick={handleSave}
                className="btn-modern-primary"
                disabled={isLoading}
              >
                {isLoading ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                    Saving...
                  </>
                ) : (
                  <>
                    <span className="mr-2">💾</span>
                    Save Changes
                  </>
                )}
              </button>
            </>
          ) : (
            <button
              onClick={() => setIsEditing(true)}
              className="btn-modern-primary"
            >
              <span className="mr-2">✏️</span>
              Edit Profile
            </button>
          )}
        </div>
      </div>

      <div className="space-y-8">
        {/* Basic Information */}
        <div className="card-modern employer-form">
          <h3 className="text-xl font-bold text-gray-900 mb-6 flex items-center">
            <span className="mr-2">🏢</span>
            Basic Information
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="form-group">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Company Name *
              </label>
              <input
                type="text"
                value={formData.name}
                onChange={(e) => handleInputChange(null, 'name', e.target.value)}
                disabled={!isEditing}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 disabled:bg-gray-50 disabled:text-gray-600"
                placeholder="Enter company name"
              />
            </div>

            <div className="form-group">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Website
              </label>
              <input
                type="url"
                value={formData.website}
                onChange={(e) => handleInputChange(null, 'website', e.target.value)}
                disabled={!isEditing}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 disabled:bg-gray-50 disabled:text-gray-600"
                placeholder="https://www.company.com"
              />
            </div>

            <div className="form-group">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Industry *
              </label>
              <select
                value={formData.industry}
                onChange={(e) => handleInputChange(null, 'industry', e.target.value)}
                disabled={!isEditing}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 disabled:bg-gray-50 disabled:text-gray-600"
              >
                <option value="">Select industry</option>
                {industryOptions.map(industry => (
                  <option key={industry} value={industry}>{industry}</option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Company Size
              </label>
              <select
                value={formData.size}
                onChange={(e) => handleInputChange(null, 'size', e.target.value)}
                disabled={!isEditing}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 disabled:bg-gray-50 disabled:text-gray-600"
              >
                <option value="">Select company size</option>
                {companySizes.map(size => (
                  <option key={size} value={size}>{size}</option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Founded Year
              </label>
              <input
                type="number"
                value={formData.founded}
                onChange={(e) => handleInputChange(null, 'founded', e.target.value)}
                disabled={!isEditing}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 disabled:bg-gray-50 disabled:text-gray-600"
                placeholder="2020"
                min="1900"
                max={new Date().getFullYear()}
              />
            </div>

            <div className="form-group">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Company Logo
              </label>
              {isEditing ? (
                <div className="space-y-3">
                  <input
                    type="file"
                    accept="image/*"
                    onChange={handleLogoUpload}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  />
                  <p className="text-xs text-gray-500">Upload a logo (max 5MB, image formats only)</p>
                </div>
              ) : (
                <div className="w-20 h-20 bg-gradient-to-br from-indigo-100 to-purple-100 rounded-xl flex items-center justify-center border-2 border-gray-200">
                  {formData.logo ? (
                    <img src={URL.createObjectURL(formData.logo)} alt="Company Logo" className="w-full h-full object-cover rounded-lg" />
                  ) : (
                    <span className="text-2xl">🏢</span>
                  )}
                </div>
              )}
            </div>
          </div>

          <div className="mt-6 form-group">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Company Description *
            </label>
            <textarea
              value={formData.description}
              onChange={(e) => handleInputChange(null, 'description', e.target.value)}
              disabled={!isEditing}
              rows={4}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 disabled:bg-gray-50 disabled:text-gray-600"
              placeholder="Describe your company, mission, and what makes it unique..."
            />
          </div>
        </div>

        {/* Location Information */}
        <div className="card-modern employer-form">
          <h3 className="text-xl font-bold text-gray-900 mb-6 flex items-center">
            <span className="mr-2">📍</span>
            Location Information
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="md:col-span-2 form-group">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Address
              </label>
              <input
                type="text"
                value={formData.location.address}
                onChange={(e) => handleInputChange('location', 'address', e.target.value)}
                disabled={!isEditing}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 disabled:bg-gray-50 disabled:text-gray-600"
                placeholder="Street address"
              />
            </div>

            <div className="form-group">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                City
              </label>
              <input
                type="text"
                value={formData.location.city}
                onChange={(e) => handleInputChange('location', 'city', e.target.value)}
                disabled={!isEditing}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 disabled:bg-gray-50 disabled:text-gray-600"
                placeholder="City"
              />
            </div>

            <div className="form-group">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                State/Province
              </label>
              <input
                type="text"
                value={formData.location.state}
                onChange={(e) => handleInputChange('location', 'state', e.target.value)}
                disabled={!isEditing}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 disabled:bg-gray-50 disabled:text-gray-600"
                placeholder="State or Province"
              />
            </div>

            <div className="form-group">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Country
              </label>
              <input
                type="text"
                value={formData.location.country}
                onChange={(e) => handleInputChange('location', 'country', e.target.value)}
                disabled={!isEditing}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 disabled:bg-gray-50 disabled:text-gray-600"
                placeholder="Country"
              />
            </div>

            <div className="form-group">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Zip/Postal Code
              </label>
              <input
                type="text"
                value={formData.location.zipCode}
                onChange={(e) => handleInputChange('location', 'zipCode', e.target.value)}
                disabled={!isEditing}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 disabled:bg-gray-50 disabled:text-gray-600"
                placeholder="Zip or Postal Code"
              />
            </div>
          </div>
        </div>

        {/* Contact Information */}
        <div className="card-modern employer-form">
          <h3 className="text-xl font-bold text-gray-900 mb-6 flex items-center">
            <span className="mr-2">📞</span>
            Contact Information
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="form-group">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Contact Email
              </label>
              <input
                type="email"
                value={formData.contact.email}
                onChange={(e) => handleInputChange('contact', 'email', e.target.value)}
                disabled={!isEditing}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 disabled:bg-gray-50 disabled:text-gray-600"
                placeholder="contact@company.com"
              />
            </div>

            <div className="form-group">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Phone Number
              </label>
              <input
                type="tel"
                value={formData.contact.phone}
                onChange={(e) => handleInputChange('contact', 'phone', e.target.value)}
                disabled={!isEditing}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 disabled:bg-gray-50 disabled:text-gray-600"
                placeholder="+1 (555) 123-4567"
              />
            </div>

            <div className="form-group">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                LinkedIn Profile
              </label>
              <input
                type="url"
                value={formData.contact.linkedIn}
                onChange={(e) => handleInputChange('contact', 'linkedIn', e.target.value)}
                disabled={!isEditing}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 disabled:bg-gray-50 disabled:text-gray-600"
                placeholder="https://linkedin.com/company/..."
              />
            </div>

            <div className="form-group">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Twitter Handle
              </label>
              <input
                type="text"
                value={formData.contact.twitter}
                onChange={(e) => handleInputChange('contact', 'twitter', e.target.value)}
                disabled={!isEditing}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 disabled:bg-gray-50 disabled:text-gray-600"
                placeholder="@company"
              />
            </div>
          </div>
        </div>

        {/* Company Culture */}
        <div className="card-modern employer-form">
          <h3 className="text-xl font-bold text-gray-900 mb-6 flex items-center">
            <span className="mr-2">🌟</span>
            Company Culture & Benefits
          </h3>
          <div className="space-y-6">
            <div className="form-group">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Company Values
              </label>
              <textarea
                value={formData.culture.values}
                onChange={(e) => handleInputChange('culture', 'values', e.target.value)}
                disabled={!isEditing}
                rows={3}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 disabled:bg-gray-50 disabled:text-gray-600"
                placeholder="Describe your company's core values and principles..."
              />
            </div>

            <div className="form-group">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Benefits & Perks
              </label>
              <textarea
                value={formData.culture.benefits}
                onChange={(e) => handleInputChange('culture', 'benefits', e.target.value)}
                disabled={!isEditing}
                rows={3}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 disabled:bg-gray-50 disabled:text-gray-600"
                placeholder="List the benefits, perks, and compensation packages you offer..."
              />
            </div>

            <div className="form-group">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Work Environment
              </label>
              <textarea
                value={formData.culture.workEnvironment}
                onChange={(e) => handleInputChange('culture', 'workEnvironment', e.target.value)}
                disabled={!isEditing}
                rows={3}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 disabled:bg-gray-50 disabled:text-gray-600"
                placeholder="Describe your work environment, culture, and team dynamics..."
              />
            </div>

            <div className="form-group">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Diversity & Inclusion
              </label>
              <textarea
                value={formData.culture.diversity}
                onChange={(e) => handleInputChange('culture', 'diversity', e.target.value)}
                disabled={!isEditing}
                rows={3}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 disabled:bg-gray-50 disabled:text-gray-600"
                placeholder="Share your commitment to diversity, inclusion, and equal opportunity..."
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default EmployerProfile;
