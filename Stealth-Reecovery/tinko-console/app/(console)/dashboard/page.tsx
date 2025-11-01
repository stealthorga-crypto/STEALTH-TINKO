"use client";

import { useQuery } from "@tanstack/react-query";
import { analytics, queryKeys } from "@/lib/api";
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip, BarChart, Bar, XAxis, YAxis, CartesianGrid } from "recharts";

const COLORS = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6', '#EC4899', '#06B6D4'];

export default function DashboardPage() {
  // Fetch analytics data
  const { data: revenueData, isLoading: isLoadingRevenue } = useQuery({
    queryKey: queryKeys.analytics.revenueRecovered(30),
    queryFn: () => analytics.getRevenueRecovered(30),
    refetchInterval: 30000, // Refresh every 30 seconds
  });

  const { data: recoveryRateData, isLoading: isLoadingRate } = useQuery({
    queryKey: queryKeys.analytics.recoveryRate(30),
    queryFn: () => analytics.getRecoveryRate(30),
    refetchInterval: 30000,
  });

  const { data: categoriesData } = useQuery({
    queryKey: queryKeys.analytics.failureCategories(),
    queryFn: () => analytics.getFailureCategories(),
    refetchInterval: 60000, // Refresh every minute
  });

  // Format currency
  const formatCurrency = (amount: number, currency: string = "USD") => {
    return new Intl.NumberFormat("en-US", {
      style: "currency",
      currency,
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount / 100); // Assuming amount is in cents
  };

  // Format percentage
  const formatPercentage = (value: number) => {
    return `${(value * 100).toFixed(1)}%`;
  };

  const totalRecovered = revenueData?.total_recovered ?? 0;
  const recoveryRate = recoveryRateData?.recovery_rate ?? 0;
  const totalFailures = recoveryRateData?.total_failures ?? 0;
  const recovered = recoveryRateData?.recovered ?? 0;

  return (
    <div className="p-8">
      <h1 className="text-3xl font-bold text-slate-900 mb-6">Dashboard</h1>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <div className="bg-white p-6 rounded-lg border border-slate-200 shadow-sm">
          <p className="text-sm text-slate-600 mb-2">Total Recovered</p>
          {isLoadingRevenue ? (
            <div className="h-9 w-32 bg-slate-200 animate-pulse rounded"></div>
          ) : (
            <>
              <p className="text-3xl font-bold text-blue-600">
                {formatCurrency(totalRecovered, revenueData?.currency)}
              </p>
              <p className="text-xs text-slate-600 mt-2">Last 30 days</p>
            </>
          )}
        </div>
        
        <div className="bg-white p-6 rounded-lg border border-slate-200 shadow-sm">
          <p className="text-sm text-slate-600 mb-2">Recovery Rate</p>
          {isLoadingRate ? (
            <div className="h-9 w-24 bg-slate-200 animate-pulse rounded"></div>
          ) : (
            <>
              <p className="text-3xl font-bold text-green-600">
                {formatPercentage(recoveryRate)}
              </p>
              <p className="text-xs text-slate-600 mt-2">
                {recovered} of {totalFailures} recovered
              </p>
            </>
          )}
        </div>
        
        <div className="bg-white p-6 rounded-lg border border-slate-200 shadow-sm">
          <p className="text-sm text-slate-600 mb-2">Active Categories</p>
          <p className="text-3xl font-bold text-slate-900">
            {categoriesData?.categories?.length ?? 0}
          </p>
          <p className="text-xs text-slate-600 mt-2">Failure types tracked</p>
        </div>
        
        <div className="bg-white p-6 rounded-lg border border-slate-200 shadow-sm">
          <p className="text-sm text-slate-600 mb-2">Failed Payments</p>
          <p className="text-3xl font-bold text-amber-600">{totalFailures}</p>
          <p className="text-xs text-slate-600 mt-2">Last 30 days</p>
        </div>
      </div>

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        {/* Failure Categories Pie Chart */}
        <div className="bg-white p-6 rounded-lg border border-slate-200 shadow-sm">
          <h2 className="text-lg font-semibold text-slate-900 mb-4">Failure Distribution</h2>
          {categoriesData?.categories && categoriesData.categories.length > 0 ? (
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={categoriesData.categories}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={(entry: any) => `${entry.category.replace(/_/g, ' ')}: ${entry.percentage.toFixed(0)}%`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="count"
                >
                  {categoriesData.categories.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip formatter={(value: any, name: any, props: any) => [`${value} failures`, props.payload.category.replace(/_/g, ' ')]} />
                <Legend 
                  formatter={(value: any, entry: any) => entry.payload?.category?.replace(/_/g, ' ') || value}
                  wrapperStyle={{ fontSize: '12px' }}
                />
              </PieChart>
            </ResponsiveContainer>
          ) : (
            <div className="h-[300px] flex items-center justify-center text-slate-400">
              No failure data available
            </div>
          )}
        </div>

        {/* Recovery Stats Bar Chart */}
        <div className="bg-white p-6 rounded-lg border border-slate-200 shadow-sm">
          <h2 className="text-lg font-semibold text-slate-900 mb-4">Recovery Overview</h2>
          {!isLoadingRate && recoveryRateData ? (
            <ResponsiveContainer width="100%" height={300}>
              <BarChart
                data={[
                  { name: 'Total Failures', value: recoveryRateData.total_failures, fill: '#F59E0B' },
                  { name: 'Recovered', value: recoveryRateData.recovered, fill: '#10B981' },
                  { name: 'Pending', value: recoveryRateData.total_failures - recoveryRateData.recovered, fill: '#EF4444' },
                ]}
              >
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="value" />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <div className="h-[300px] flex items-center justify-center">
              <div className="space-y-2 w-full">
                <div className="h-8 bg-slate-200 animate-pulse rounded"></div>
                <div className="h-8 bg-slate-200 animate-pulse rounded"></div>
                <div className="h-8 bg-slate-200 animate-pulse rounded"></div>
              </div>
            </div>
          )}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white p-6 rounded-lg border border-slate-200 shadow-sm">
          <h2 className="text-lg font-semibold text-slate-900 mb-4">Failure Categories</h2>
          {categoriesData?.categories && categoriesData.categories.length > 0 ? (
            <div className="space-y-3">
              {categoriesData.categories.slice(0, 5).map((category) => (
                <div key={category.category} className="flex items-center justify-between">
                  <div className="flex items-start gap-3">
                    <div className="w-2 h-2 bg-blue-500 rounded-full mt-2"></div>
                    <div>
                      <p className="text-sm font-medium text-slate-900 capitalize">
                        {category.category.replace(/_/g, " ")}
                      </p>
                      <p className="text-xs text-slate-600">{category.count} failures</p>
                    </div>
                  </div>
                  <span className="text-sm font-semibold text-slate-700">
                    {category.percentage.toFixed(1)}%
                  </span>
                </div>
              ))}
            </div>
          ) : (
            <div className="space-y-3">
              <div className="flex items-start gap-3">
                <div className="w-2 h-2 bg-slate-300 rounded-full mt-2"></div>
                <div>
                  <p className="text-sm text-slate-500">No failure data yet</p>
                  <p className="text-xs text-slate-400">Data will appear once payments are processed</p>
                </div>
              </div>
            </div>
          )}
        </div>

        <div className="bg-white p-6 rounded-lg border border-slate-200 shadow-sm">
          <h2 className="text-lg font-semibold text-slate-900 mb-4">Quick Stats</h2>
          <div className="space-y-4">
            <div className="flex items-center justify-between pb-3 border-b border-slate-100">
              <span className="text-sm text-slate-600">Total Failures</span>
              <span className="text-lg font-semibold text-slate-900">{totalFailures}</span>
            </div>
            <div className="flex items-center justify-between pb-3 border-b border-slate-100">
              <span className="text-sm text-slate-600">Recovered</span>
              <span className="text-lg font-semibold text-green-600">{recovered}</span>
            </div>
            <div className="flex items-center justify-between pb-3 border-b border-slate-100">
              <span className="text-sm text-slate-600">Pending</span>
              <span className="text-lg font-semibold text-amber-600">
                {totalFailures - recovered}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-slate-600">Success Rate</span>
              <span className="text-lg font-semibold text-blue-600">
                {formatPercentage(recoveryRate)}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
