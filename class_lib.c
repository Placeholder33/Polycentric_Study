#include <stdio.h>
#include <stdlib.h>
#include "class_lib.h"
/*
double submitjana(int l1, int l2, double M[N][N], int q, int i, int j)
{
    int f, c;
    double sum = 0;
    for(f=0; f<q; f++){
        for(c=0; c<q; c++){
            //afegim cada valor a values
            sum += M[i*q + f][j*q + c];
        }
    }
    return (sum/(q*q));
}

void gridificator(int l1, int l2, double M[N][N], int n, int m, double** G){
	if(N >= L){
		q = N/L;
		for(int i=0; i<L; i++)
			for(int j=0; j<L; j++)
				G[i][j] = submitjana(N, M, q, i, j);
	}
*/

/* SLICING */

double max_search(int n,int m,double *M){
    double max = M[0];
    for(int i=0;i<n;i++)
        for(int j=0;j<m;j++)
            if (M[m*i+j] > max) max = M[m*i+j];
    return max;
}

void cut(int n, int m, double cutoff, double *M, int *A){
	for(int i=0;i<n;i++)
		for(int j=0;j<n;j++)
			if (M[i*m+j] > cutoff) {A[i*m+j] = 1;} else {A[i*m+j] = 0;}
}

/*GRAPHING*/

int matgraf(int n, int m, int *A, int (*P)[2]){
    int len_p=0;
    for(int i=0; i<n; i++){
        for(int j=0; j<m; j++){
            if(A[i*m+j]==1){ // Term is 1
                if(i != 0){
                    if(A[(i-1)*m+j]==1){ // Check row above
                        P[len_p][1]=i*m +j;
                        P[len_p][0]=(i-1)*m + j;
                        len_p++;
                    }
                }
                if(j != 0){
                    if(A[i*m+(j-1)]==1){ // Check column to the left
                        P[len_p][1]=i*m + j;
                        P[len_p][0]=i*m + (j-1);
                        len_p++;
                    }
                }
            }
        }
    }
    return len_p;
}

/* SLICE & DICE */

int slice_graph(int n, int m, double cutoff, double *M, int (*p)[2]){
        /* SLICING */
	int *A = malloc(n*m*sizeof(int));
        cut(n,m,cutoff,M,A);
        /* GRAPHING */
	int x =  matgraf(n,m,A,p);	
	free(A);
	return x;
}

