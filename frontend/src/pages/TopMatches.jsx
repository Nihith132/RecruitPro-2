import React, { useState, useEffect } from 'react';
import {
  Container,
  Typography,
  Box,
  Grid,
  Card,
  CardContent,
  CircularProgress,
  Chip,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Button,
  Divider,
  Stack,
} from '@mui/material';
import {
  Description as FileIcon,
  Visibility as ViewIcon,
  EmojiEvents as TrophyIcon,
  CheckCircle as CheckIcon,
  Cancel as MissingIcon,
} from '@mui/icons-material';
import axios from 'axios';
import { useAuth } from '../context/AuthContext';
import { API_BASE_URL } from '../config/firebase';
import { toast } from 'react-toastify';
import { motion } from 'framer-motion';

const TopMatches = () => {
  const { token } = useAuth();
  const [jds, setJds] = useState([]);
  const [selectedJD, setSelectedJD] = useState('');
  const [selectedJDDetails, setSelectedJDDetails] = useState(null);
  const [matches, setMatches] = useState([]);
  const [loading, setLoading] = useState(true);
  const [minScore, setMinScore] = useState(0);

  useEffect(() => {
    fetchJDs();
  }, []);

  useEffect(() => {
    if (selectedJD) {
      fetchMatches();
      const jdDetails = jds.find(jd => jd.jd_id === selectedJD);
      setSelectedJDDetails(jdDetails);
    }
  }, [selectedJD, minScore]);

  const fetchJDs = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/jds/`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setJds(response.data);
      if (response.data.length > 0) {
        setSelectedJD(response.data[0].jd_id);
      } else {
        setLoading(false);
      }
    } catch (error) {
      console.error('Failed to fetch job descriptions:', error);
      toast.error('Failed to fetch job descriptions');
      setLoading(false);
    }
  };

  const fetchMatches = async () => {
    if (!selectedJD) return;
    setLoading(true);
    try {
      const response = await axios.get(
        `${API_BASE_URL}/api/top-matches/${selectedJD}?min_score=${minScore}`,
        {
          headers: { Authorization: `Bearer ${token}` }
        }
      );
      console.log('Matches fetched:', response.data);
      setMatches(Array.isArray(response.data) ? response.data : []);
    } catch (error) {
      console.error('Failed to fetch matches:', error);
      toast.error('Failed to fetch matches');
      setMatches([]);
    } finally {
      setLoading(false);
    }
  };

  const handleViewResume = async (candidateId) => {
    try {
      const response = await axios.get(
        `${API_BASE_URL}/api/candidates/download/${candidateId}`,
        {
          headers: { Authorization: `Bearer ${token}` },
          responseType: 'blob'
        }
      );
      
      const blob = new Blob([response.data], { type: response.headers['content-type'] });
      const blobUrl = window.URL.createObjectURL(blob);
      window.open(blobUrl, '_blank');
      
      setTimeout(() => window.URL.revokeObjectURL(blobUrl), 100);
    } catch (error) {
      console.error('Failed to open resume:', error);
      toast.error('Failed to open resume file');
    }
  };

  const handleViewJD = async (jdId) => {
    try {
      const response = await axios.get(
        `${API_BASE_URL}/api/jds/download/${jdId}`,
        {
          headers: { Authorization: `Bearer ${token}` },
          responseType: 'blob'
        }
      );
      
      const blob = new Blob([response.data], { type: response.headers['content-type'] });
      const blobUrl = window.URL.createObjectURL(blob);
      window.open(blobUrl, '_blank');
      
      setTimeout(() => window.URL.revokeObjectURL(blobUrl), 100);
    } catch (error) {
      console.error('Failed to open JD file:', error);
      toast.error('Failed to open JD file');
    }
  };

  const handleRunMatching = async () => {
    if (!selectedJD) return;
    
    try {
      setLoading(true);
      toast.info('Running AI matching... This may take a few moments');
      
      await axios.post(
        `${API_BASE_URL}/api/match`,
        { jd_id: selectedJD },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      
      toast.success('Matching completed! Refreshing results...');
      await fetchMatches();
    } catch (error) {
      console.error('Failed to run matching:', error);
      toast.error('Failed to run matching: ' + (error.response?.data?.detail || error.message));
    } finally {
      setLoading(false);
    }
  };

  const getScoreColor = (score) => {
    if (score >= 80) return 'success';
    if (score >= 60) return 'info';
    if (score >= 40) return 'warning';
    return 'error';
  };

  const getScoreLabel = (score) => {
    if (score >= 80) return 'Outstanding';
    if (score >= 70) return 'Excellent';
    if (score >= 60) return 'Very Good';
    if (score >= 50) return 'Good';
    if (score >= 40) return 'Fair';
    return 'Needs Review';
  };

  const getMedalIcon = (index) => {
    if (index === 0) return '🥇';
    if (index === 1) return '🥈';
    if (index === 2) return '🥉';
    return `#${index + 1}`;
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="80vh">
        <CircularProgress size={50} />
      </Box>
    );
  }

  return (
    <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, ease: [0.4, 0, 0.2, 1] }}
      >
        <Box mb={4}>
          <Typography variant="h4" fontWeight="bold" gutterBottom>
            🎯 Top Matches
          </Typography>
          <Typography color="text.secondary" mb={3}>
            AI-ranked candidates sorted by match score (best to lowest)
          </Typography>

          {/* Filters */}
          {jds.length > 0 && (
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.4, delay: 0.1, ease: [0.4, 0, 0.2, 1] }}
            >
              <Card sx={{ mb: 3, bgcolor: 'background.paper' }}>
                <CardContent>
                  <Grid container spacing={2} alignItems="center">
                    <Grid item xs={12} md={6}>
                      <FormControl fullWidth size="small">
                        <InputLabel>Select Job Description</InputLabel>
                        <Select
                          value={selectedJD}
                          label="Select Job Description"
                          onChange={(e) => setSelectedJD(e.target.value)}
                        >
                          {jds.map((jd) => (
                            <MenuItem key={jd.jd_id} value={jd.jd_id}>
                              {jd.job_title} {jd.company && `- ${jd.company}`}
                            </MenuItem>
                          ))}
                        </Select>
                      </FormControl>
                    </Grid>
                    <Grid item xs={12} md={4}>
                      <FormControl fullWidth size="small">
                        <InputLabel>Minimum Score Filter</InputLabel>
                        <Select
                          value={minScore}
                          label="Minimum Score Filter"
                          onChange={(e) => setMinScore(e.target.value)}
                        >
                          <MenuItem value={0}>All Candidates (0%+)</MenuItem>
                          <MenuItem value={40}>Fair Match (40%+)</MenuItem>
                          <MenuItem value={50}>Good Match (50%+)</MenuItem>
                          <MenuItem value={60}>Very Good (60%+)</MenuItem>
                          <MenuItem value={70}>Excellent (70%+)</MenuItem>
                          <MenuItem value={80}>Outstanding (80%+)</MenuItem>
                        </Select>
                      </FormControl>
                    </Grid>
                    <Grid item xs={12} md={2}>
                      <Button
                        fullWidth
                        variant="contained"
                        color="success"
                        onClick={handleRunMatching}
                        disabled={!selectedJD || loading}
                      >
                        {loading ? 'Matching...' : 'Run Matching'}
                      </Button>
                    </Grid>
                  </Grid>
                  
                  {/* View JD Button - Secondary row */}
                  <Box mt={2} display="flex" justifyContent="flex-end">
                    <Button
                      variant="outlined"
                      size="small"
                      startIcon={<ViewIcon />}
                      onClick={() => selectedJD && handleViewJD(selectedJD)}
                      disabled={!selectedJD}
                    >
                      View JD File
                    </Button>
                  </Box>
                </CardContent>
              </Card>
            </motion.div>
          )}

          {/* JD Details Card */}
          {selectedJDDetails && (
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.4, delay: 0.2, ease: [0.4, 0, 0.2, 1] }}
            >
              <Card 
                sx={{ 
                  mb: 3, 
                  background: (theme) => theme.palette.mode === 'dark' 
                    ? 'linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%)'
                    : 'linear-gradient(135deg, #3b82f6 0%, #60a5fa 100%)',
                  color: 'white'
                }}
              >
                <CardContent>
                  <Box display="flex" justifyContent="space-between" alignItems="start">
                    <Box flex={1}>
                      <Typography variant="h5" fontWeight="700" gutterBottom>
                        {selectedJDDetails.job_title}
                      </Typography>
                      <Stack direction="row" spacing={2} flexWrap="wrap" mb={2}>
                        {selectedJDDetails.company && (
                          <Chip
                            label={selectedJDDetails.company}
                            size="small"
                            sx={{ bgcolor: 'rgba(255,255,255,0.2)', color: 'white' }}
                          />
                        )}
                        {selectedJDDetails.location && (
                          <Chip
                            label={selectedJDDetails.location}
                            size="small"
                            sx={{ bgcolor: 'rgba(255,255,255,0.2)', color: 'white' }}
                          />
                        )}
                        {selectedJDDetails.experience_required && (
                          <Chip
                            label={`Exp: ${selectedJDDetails.experience_required}`}
                            size="small"
                            sx={{ bgcolor: 'rgba(255,255,255,0.2)', color: 'white' }}
                          />
                        )}
                      </Stack>
                      {selectedJDDetails.required_skills && selectedJDDetails.required_skills.length > 0 && (
                        <Box>
                          <Typography variant="caption" sx={{ opacity: 0.9, display: 'block', mb: 1 }}>
                            Required Skills:
                          </Typography>
                          <Box display="flex" flexWrap="wrap" gap={0.5}>
                            {selectedJDDetails.required_skills.slice(0, 8).map((skill, idx) => (
                              <Chip
                                key={idx}
                                label={skill}
                                size="small"
                                sx={{ bgcolor: 'rgba(255,255,255,0.25)', color: 'white', fontWeight: 600 }}
                              />
                            ))}
                            {selectedJDDetails.required_skills.length > 8 && (
                              <Chip
                                label={`+${selectedJDDetails.required_skills.length - 8} more`}
                                size="small"
                                sx={{ bgcolor: 'rgba(255,255,255,0.15)', color: 'white' }}
                              />
                            )}
                          </Box>
                        </Box>
                      )}
                    </Box>
                  </Box>
                </CardContent>
              </Card>
            </motion.div>
          )}
        </Box>
      </motion.div>

      {/* Results Section */}
      {jds.length === 0 ? (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.5 }}
        >
          <Card>
            <CardContent sx={{ textAlign: 'center', py: 8 }}>
              <FileIcon sx={{ fontSize: 80, color: 'text.secondary', mb: 2 }} />
              <Typography variant="h6" color="text.secondary" gutterBottom>
                No Job Descriptions Yet
              </Typography>
              <Typography color="text.secondary">
                Upload job descriptions to see candidate matches
              </Typography>
            </CardContent>
          </Card>
        </motion.div>
      ) : matches.length === 0 ? (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.5 }}
        >
          <Card>
            <CardContent sx={{ textAlign: 'center', py: 8 }}>
              <Typography variant="h6" color="text.secondary" gutterBottom>
                {minScore > 0 
                  ? `No candidates found with ${minScore}%+ match score`
                  : 'No matches found for this job description'}
              </Typography>
              <Typography color="text.secondary" mb={2}>
                {minScore > 0 
                  ? 'Try lowering the minimum score filter'
                  : 'Upload candidate resumes or select a different JD'}
              </Typography>
            </CardContent>
          </Card>
        </motion.div>
      ) : (
        <>
          {/* Results Count */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4, delay: 0.1 }}
          >
            <Box mb={3} display="flex" justifyContent="space-between" alignItems="center">
              <Typography variant="h6" fontWeight="600">
                {matches.length} Candidate{matches.length !== 1 ? 's' : ''} Found
                {minScore > 0 && ` (${minScore}%+ match)`}
              </Typography>
              <Chip
                icon={<TrophyIcon />}
                label="Sorted by Best Match"
                color="primary"
                variant="outlined"
              />
            </Box>
          </motion.div>

          {/* Matches List */}
          <Stack spacing={2}>
            {matches.map((match, index) => (
              <motion.div
                key={match.candidate_id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ 
                  duration: 0.4, 
                  delay: index * 0.05,
                  ease: [0.4, 0, 0.2, 1]
                }}
              >
                <Card
                  sx={{
                    border: index < 3 ? 2 : 1,
                    borderColor: index === 0 ? 'warning.main' : index === 1 ? 'grey.400' : index === 2 ? '#cd7f32' : 'divider',
                    boxShadow: index < 3 ? 4 : 1,
                    transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                    '&:hover': {
                      boxShadow: 6,
                      transform: 'translateY(-4px)'
                    }
                  }}
                >
                  <CardContent>
                    <Grid container spacing={3}>
                      {/* Left: Rank & Score */}
                      <Grid item xs={12} md={2}>
                        <Box textAlign="center">
                          <Typography variant="h3" fontWeight="bold" sx={{ fontSize: '2.5rem', mb: 1 }}>
                            {getMedalIcon(index)}
                          </Typography>
                          <Chip
                            label={`${Math.round(match.total_score)}%`}
                            color={getScoreColor(match.total_score)}
                            sx={{
                              fontWeight: 'bold',
                              fontSize: '1.1rem',
                              height: 36,
                              mb: 1
                            }}
                          />
                          <Typography variant="caption" display="block" color="text.secondary">
                            {getScoreLabel(match.total_score)}
                          </Typography>
                        </Box>
                      </Grid>

                      {/* Middle: Candidate Info */}
                      <Grid item xs={12} md={7}>
                        <Box>
                          <Box display="flex" justifyContent="space-between" alignItems="start" mb={2}>
                            <Box>
                              <Typography variant="h5" fontWeight="700" gutterBottom>
                                {match.name || 'Unknown Candidate'}
                              </Typography>
                              <Typography variant="body2" color="text.secondary" gutterBottom>
                                {match.designation || 'No designation specified'}
                              </Typography>
                              {match.experience && (
                                <Chip
                                  label={`Experience: ${match.experience}`}
                                  size="small"
                                  variant="outlined"
                                  sx={{ mt: 0.5 }}
                                />
                              )}
                            </Box>
                          </Box>

                          <Divider sx={{ my: 2 }} />

                          {/* Skills Section */}
                          <Grid container spacing={2}>
                            {/* Matched Skills */}
                            {match.skills_matched && match.skills_matched.length > 0 && (
                              <Grid item xs={12} md={6}>
                                <Box display="flex" alignItems="center" gap={1} mb={1}>
                                  <CheckIcon color="success" fontSize="small" />
                                  <Typography variant="caption" fontWeight="600" color="success.main">
                                    Matched Skills ({match.skills_matched.length})
                                  </Typography>
                                </Box>
                                <Box display="flex" flexWrap="wrap" gap={0.5}>
                                  {match.skills_matched.slice(0, 6).map((skill, idx) => (
                                    <Chip
                                      key={idx}
                                      label={skill}
                                      size="small"
                                      color="success"
                                      sx={{ fontSize: '0.75rem' }}
                                    />
                                  ))}
                                  {match.skills_matched.length > 6 && (
                                    <Chip
                                      label={`+${match.skills_matched.length - 6}`}
                                      size="small"
                                      color="success"
                                      variant="outlined"
                                    />
                                  )}
                                </Box>
                              </Grid>
                            )}

                            {/* Missing Skills */}
                            {match.skills_missing && match.skills_missing.length > 0 && (
                              <Grid item xs={12} md={6}>
                                <Box display="flex" alignItems="center" gap={1} mb={1}>
                                  <MissingIcon color="error" fontSize="small" />
                                  <Typography variant="caption" fontWeight="600" color="error.main">
                                    Missing Skills ({match.skills_missing.length})
                                  </Typography>
                                </Box>
                                <Box display="flex" flexWrap="wrap" gap={0.5}>
                                  {match.skills_missing.slice(0, 6).map((skill, idx) => (
                                    <Chip
                                      key={idx}
                                      label={skill}
                                      size="small"
                                      color="error"
                                      variant="outlined"
                                      sx={{ fontSize: '0.75rem' }}
                                    />
                                  ))}
                                  {match.skills_missing.length > 6 && (
                                    <Chip
                                      label={`+${match.skills_missing.length - 6}`}
                                      size="small"
                                      color="error"
                                      variant="outlined"
                                    />
                                  )}
                                </Box>
                              </Grid>
                            )}
                          </Grid>
                        </Box>
                      </Grid>

                      {/* Right: Actions & Breakdown */}
                      <Grid item xs={12} md={3}>
                        <Stack spacing={2}>
                          {/* View Resume Button */}
                          <Button
                            fullWidth
                            variant="contained"
                            startIcon={<ViewIcon />}
                            onClick={() => handleViewResume(match.candidate_id)}
                            sx={{
                              bgcolor: 'primary.main',
                              '&:hover': {
                                bgcolor: 'primary.dark',
                              }
                            }}
                          >
                            View Resume
                          </Button>

                          <Divider />

                          {/* Score Breakdown */}
                          <Box>
                            <Typography variant="caption" color="text.secondary" fontWeight="600" display="block" mb={1}>
                              Score Breakdown:
                            </Typography>
                            <Stack spacing={1}>
                              <Box>
                                <Box display="flex" justifyContent="space-between" mb={0.5}>
                                  <Typography variant="caption">Skills</Typography>
                                  <Typography variant="caption" fontWeight="700">
                                    {Math.round(match.skills_score || 0)}%
                                  </Typography>
                                </Box>
                                <Box sx={{ width: '100%', bgcolor: 'grey.200', borderRadius: 1, height: 6 }}>
                                  <Box
                                    sx={{
                                      width: `${match.skills_score || 0}%`,
                                      bgcolor: getScoreColor(match.skills_score) + '.main',
                                      height: '100%',
                                      borderRadius: 1,
                                      transition: 'width 0.5s'
                                    }}
                                  />
                                </Box>
                              </Box>

                              <Box>
                                <Box display="flex" justifyContent="space-between" mb={0.5}>
                                  <Typography variant="caption">Experience</Typography>
                                  <Typography variant="caption" fontWeight="700">
                                    {Math.round(match.experience_score || 0)}%
                                  </Typography>
                                </Box>
                                <Box sx={{ width: '100%', bgcolor: 'grey.200', borderRadius: 1, height: 6 }}>
                                  <Box
                                    sx={{
                                      width: `${match.experience_score || 0}%`,
                                      bgcolor: getScoreColor(match.experience_score) + '.main',
                                      height: '100%',
                                      borderRadius: 1,
                                      transition: 'width 0.5s'
                                    }}
                                  />
                                </Box>
                              </Box>

                              <Box>
                                <Box display="flex" justifyContent="space-between" mb={0.5}>
                                  <Typography variant="caption">Education</Typography>
                                  <Typography variant="caption" fontWeight="700">
                                    {Math.round(match.education_score || 0)}%
                                  </Typography>
                                </Box>
                                <Box sx={{ width: '100%', bgcolor: 'grey.200', borderRadius: 1, height: 6 }}>
                                  <Box
                                    sx={{
                                      width: `${match.education_score || 0}%`,
                                      bgcolor: getScoreColor(match.education_score) + '.main',
                                      height: '100%',
                                      borderRadius: 1,
                                      transition: 'width 0.5s'
                                    }}
                                  />
                                </Box>
                              </Box>

                              <Box>
                                <Box display="flex" justifyContent="space-between" mb={0.5}>
                                  <Typography variant="caption">Certifications</Typography>
                                  <Typography variant="caption" fontWeight="700">
                                    {Math.round(match.certifications_score || 0)}%
                                  </Typography>
                                </Box>
                                <Box sx={{ width: '100%', bgcolor: 'grey.200', borderRadius: 1, height: 6 }}>
                                  <Box
                                    sx={{
                                      width: `${match.certifications_score || 0}%`,
                                      bgcolor: getScoreColor(match.certifications_score) + '.main',
                                      height: '100%',
                                      borderRadius: 1,
                                      transition: 'width 0.5s'
                                    }}
                                  />
                                </Box>
                              </Box>
                            </Stack>
                          </Box>
                        </Stack>
                      </Grid>
                    </Grid>
                  </CardContent>
                </Card>
              </motion.div>
            ))}
          </Stack>
        </>
      )}
    </Container>
  );
};

export default TopMatches;
