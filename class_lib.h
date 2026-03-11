#ifndef MATH_UTILS_H
#define MATH_UTILS_H

void gridificator(int N, double M[N][N], int L, double** G);
double submitjana(int N, double M[N][N], int q, int i, int j);
double max_search(int n,int m,double *M);
void cut(int n, int m, double cutoff, double *M, int *A);
int matgraf(int n, int m, int *A, int (*P)[2]);
int slice_graph(int n, int m, double cutoff, double *M, int (*p)[2]);
	
#endif

