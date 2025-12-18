import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Grid,
  Card,
  CardContent,
  Typography,
  Button,
  CircularProgress,
  Chip,
  useTheme as useMuiTheme
} from '@mui/material';
import {
  People as PeopleIcon,
  Description as DescriptionIcon,
  TrendingUp as TrendingUpIcon,
  Stars as StarsIcon,
  CloudUpload as UploadIcon
} from '@mui/icons-material';
import { motion } from 'framer-motion';
import axios from 'axios';
import { useAuth } from '../context/AuthContext';
import { API_BASE_URL } from '../config/firebase';
import { useNavigate } from 'react-router-dom';
import { toast } from 'react-toastify';

const StatCard = ({ title, value, icon, color }) => {
  const theme = useMuiTheme();
  
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
    >
      <Card sx={{ height: '100%' }}>
        <CardContent>
          <Box display="flex" justifyContent="space-between" alignItems="center">
            <Box>
              <Typography color="text.secondary" variant="body2" gutterBottom>
                {title}
              </Typography>
              <Typography variant="h4" fontWeight="bold">
                {value}
              </Typography>
            </Box>
            <Box
              sx={{
                width: 60,
                height: 60,
                borderRadius: 2,
                bgcolor: `${color}.100`,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center'
              }}
            >
              {React.cloneElement(icon, {
                sx: { fontSize: 32, color: `${color}.main` }
              })}
            </Box>
          </Box>
        </CardContent>
      </Card>
    </motion.div>
  );
};

const Dashboard = () => {
  const { token } = useAuth();
  const navigate = useNavigate();
  const theme = useMuiTheme();
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchAnalytics();
  }, []);

  const fetchAnalytics = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/analytics/dashboard`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setAnalytics(response.data);
    } catch (error) {
      console.error('Error fetching analytics:', error);
      toast.error('Failed to load analytics');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="80vh">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
      {/* Header */}
      <Box mb={4}>
        <Typography variant="h4" fontWeight="bold" gutterBottom>
          Dashboard
        </Typography>
        <Typography color="text.secondary">
          Overview of your recruitment pipeline
        </Typography>
      </Box>

      {/* Stats Cards */}
      <Grid container spacing={3} mb={4}>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Total Candidates"
            value={analytics?.total_candidates || 0}
            icon={<PeopleIcon />}
            color="primary"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Job Descriptions"
            value={analytics?.total_jds || 0}
            icon={<DescriptionIcon />}
            color="secondary"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="High Matches (50%+)"
            value={analytics?.high_scoring_matches || 0}
            icon={<StarsIcon />}
            color="success"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Total Matches"
            value={analytics?.total_matches || 0}
            icon={<TrendingUpIcon />}
            color="warning"
          />
        </Grid>
      </Grid>

      {/* Quick Actions */}
      <Card sx={{ mb: 4 }}>
        <CardContent>
          <Typography variant="h6" fontWeight="600" gutterBottom>
            Quick Actions
          </Typography>
          <Box display="flex" gap={2} flexWrap="wrap" mt={2}>
            <Button
              variant="contained"
              startIcon={<UploadIcon />}
              onClick={() => navigate('/candidates')}
            >
              Upload Resumes
            </Button>
            <Button
              variant="contained"
              startIcon={<UploadIcon />}
              onClick={() => navigate('/job-descriptions')}
            >
              Upload Job Descriptions
            </Button>
            <Button
              variant="outlined"
              onClick={() => navigate('/top-matches')}
            >
              View Top Matches
            </Button>
          </Box>
        </CardContent>
      </Card>

      {/* Charts */}
      <Grid container spacing={3}>
        {/* Top Matches Chart - Full Width */}
        <Grid item xs={12}>
          <Card sx={{ 
            background: (theme) => theme.palette.mode === 'dark' 
              ? 'linear-gradient(135deg, #1a1a2e 0%, #16213e 100%)'
              : 'linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%)',
          }}>
            <CardContent>
              <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
                <Box>
                  <Typography variant="h5" fontWeight="700" gutterBottom>
                    🏆 Top 5 Candidate Matches
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Highest scoring candidate-JD combinations
                  </Typography>
                </Box>
                <Button
                  variant="outlined"
                  size="small"
                  onClick={() => navigate('/top-matches')}
                  sx={{ textTransform: 'none' }}
                >
                  View All Matches
                </Button>
              </Box>
              
              {analytics?.top_matches?.length > 0 ? (
                <Box sx={{ width: '100%', mt: 2 }}>
                  {analytics.top_matches.map((match, index) => (
                    <motion.div
                      key={index}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ duration: 0.4, delay: index * 0.1 }}
                    >
                      <Box sx={{ mb: 3 }}>
                        {/* Header with rank, name, and score */}
                        <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
                          <Box display="flex" alignItems="center" gap={2}>
                            <Typography 
                              variant="h4" 
                              fontWeight="bold" 
                              sx={{ 
                                color: index === 0 ? '#FFD700' : index === 1 ? '#C0C0C0' : index === 2 ? '#CD7F32' : 'text.secondary',
                                minWidth: 40
                              }}
                            >
                              {index === 0 ? '🥇' : index === 1 ? '🥈' : index === 2 ? '🥉' : `#${index + 1}`}
                            </Typography>
                            <Box>
                              <Typography variant="h6" fontWeight="600">
                                {match.candidate_name}
                              </Typography>
                              <Typography variant="body2" color="text.secondary">
                                {match.jd_name}
                              </Typography>
                            </Box>
                          </Box>
                          <Chip
                            label={`${match.score}%`}
                            color={
                              match.score >= 80 ? 'success' : 
                              match.score >= 60 ? 'info' : 
                              match.score >= 40 ? 'warning' : 'error'
                            }
                            sx={{ 
                              fontWeight: 'bold', 
                              fontSize: '1rem',
                              minWidth: 80,
                              height: 36
                            }}
                          />
                        </Box>
                        
                        {/* Progress Bar */}
                        <Box sx={{ position: 'relative', width: '100%', height: 12, bgcolor: 'grey.200', borderRadius: 2, overflow: 'hidden' }}>
                          <motion.div
                            initial={{ width: 0 }}
                            animate={{ width: `${match.score}%` }}
                            transition={{ duration: 0.8, delay: index * 0.1 + 0.2, ease: "easeOut" }}
                            style={{
                              height: '100%',
                              background: match.score >= 80 
                                ? 'linear-gradient(90deg, #10b981 0%, #059669 100%)'
                                : match.score >= 60
                                ? 'linear-gradient(90deg, #3b82f6 0%, #2563eb 100%)'
                                : match.score >= 40
                                ? 'linear-gradient(90deg, #f59e0b 0%, #d97706 100%)'
                                : 'linear-gradient(90deg, #ef4444 0%, #dc2626 100%)',
                              borderRadius: '8px',
                              boxShadow: match.score >= 60 ? '0 2px 8px rgba(59, 130, 246, 0.3)' : 'none'
                            }}
                          />
                        </Box>
                      </Box>
                    </motion.div>
                  ))}
                </Box>
              ) : (
                <Box display="flex" flexDirection="column" justifyContent="center" alignItems="center" height={300} sx={{ opacity: 0.6 }}>
                  <TrendingUpIcon sx={{ fontSize: 80, color: 'text.secondary', mb: 2 }} />
                  <Typography variant="h6" color="text.secondary" gutterBottom>
                    No Matches Yet
                  </Typography>
                  <Typography variant="body2" color="text.secondary" textAlign="center" mb={2}>
                    Run matching to see your top candidate-JD combinations here
                  </Typography>
                  <Button
                    variant="contained"
                    onClick={() => navigate('/top-matches')}
                    sx={{ mt: 1 }}
                  >
                    Go to Top Matches
                  </Button>
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Getting Started (if no data) */}
      {analytics?.total_candidates === 0 && analytics?.total_jds === 0 && (
        <Card sx={{ mt: 4, bgcolor: 'primary.50' }}>
          <CardContent>
            <Typography variant="h6" fontWeight="600" gutterBottom>
              🚀 Get Started with RecruitPro 2
            </Typography>
            <Typography color="text.secondary" paragraph>
              Start by uploading candidate resumes and job descriptions to see intelligent matching in action.
            </Typography>
            <Box display="flex" gap={2}>
              <Button
                variant="contained"
                onClick={() => navigate('/candidates')}
              >
                Upload First Resume
              </Button>
              <Button
                variant="outlined"
                onClick={() => navigate('/job-descriptions')}
              >
                Add Job Description
              </Button>
            </Box>
          </CardContent>
        </Card>
      )}
    </Container>
  );
};

export default Dashboard;
