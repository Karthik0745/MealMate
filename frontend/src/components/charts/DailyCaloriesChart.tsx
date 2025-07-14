import React from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler,
} from 'chart.js';
import { Line } from 'react-chartjs-2';
import { DailyCaloriesData } from '../../types';
import { dashboardService } from '../../services/dashboard';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

interface DailyCaloriesChartProps {
  data: DailyCaloriesData;
  height?: number;
}

const DailyCaloriesChart: React.FC<DailyCaloriesChartProps> = ({ 
  data, 
  height = 300 
}) => {
  const chartData = dashboardService.formatDailyCaloriesForChart(data);

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top' as const,
        labels: {
          usePointStyle: true,
          pointStyle: 'circle',
          padding: 20,
          font: {
            size: 14,
          },
        },
      },
      title: {
        display: true,
        text: `Daily Calories - ${data.period}`,
        font: {
          size: 16,
          weight: 'bold',
        },
        padding: {
          bottom: 20,
        },
      },
      tooltip: {
        mode: 'index' as const,
        intersect: false,
        backgroundColor: 'rgba(0, 0, 0, 0.8)',
        titleColor: '#ffffff',
        bodyColor: '#ffffff',
        borderColor: '#e5e7eb',
        borderWidth: 1,
        cornerRadius: 8,
        padding: 12,
        callbacks: {
          label: function(context: any) {
            const label = context.dataset.label || '';
            const value = context.parsed.y;
            return `${label}: ${value} calories`;
          },
          afterBody: function(tooltipItems: any) {
            const dataPoint = data.daily_data[tooltipItems[0].dataIndex];
            return [`Meals logged: ${dataPoint.meal_count}`];
          },
        },
      },
    },
    scales: {
      x: {
        display: true,
        title: {
          display: true,
          text: 'Date',
          font: {
            size: 12,
            weight: 'bold',
          },
        },
        grid: {
          display: false,
        },
      },
      y: {
        display: true,
        title: {
          display: true,
          text: 'Calories',
          font: {
            size: 12,
            weight: 'bold',
          },
        },
        beginAtZero: true,
        grid: {
          color: 'rgba(0, 0, 0, 0.1)',
        },
      },
    },
    interaction: {
      mode: 'nearest' as const,
      axis: 'x' as const,
      intersect: false,
    },
    elements: {
      point: {
        radius: 4,
        hoverRadius: 8,
      },
      line: {
        tension: 0.3,
      },
    },
  };

  return (
    <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
      <div style={{ height: `${height}px` }}>
        <Line data={chartData} options={options} />
      </div>
      
      {/* Chart summary */}
      <div className="mt-4 flex justify-between items-center text-sm text-gray-600">
        <div>
          <span className="font-medium">
            Total period: {data.daily_data.reduce((sum, day) => sum + day.calories, 0).toLocaleString()} calories
          </span>
        </div>
        <div>
          <span className="font-medium">
            Average: {Math.round(data.daily_data.reduce((sum, day) => sum + day.calories, 0) / data.daily_data.length).toLocaleString()} cal/day
          </span>
        </div>
      </div>
    </div>
  );
};

export default DailyCaloriesChart;