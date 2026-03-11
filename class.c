#include <stdio.h>
#include <stdlib.h>
#include "class_lib.h"
#include <math.h>

int main(){
	/* PARAMETERS */
	const int n = 3, m = 3;
	double eps = 0.5;
	double *M = malloc(n*m*sizeof(double));
	/* TEST MATRIX */
	for(int i = 0; i < n; i++)
		for(int j = 0; j < n; j++)
			M[i*m+j] = 0; //abs((n-2*i)+(m-2*j));
	M[0] = 1;
	M[1] = 1;
	M[2] = 1;
	/* SLICE */
	double max=max_search(n,m,M);
	int k = (int)((max/eps) + 1);
        int (**p)[2] = malloc(k*sizeof(*p));
        int c = 0;
	for(double l = 0; l < max; l+=eps){	
		p[c] = malloc(2*n*m * sizeof(*p[c]));
		if (!p[c]) { perror("malloc"); exit(1); }
		slice_graph(n,m,l,M,p[c]);
		fprintf(stdout,"\n");
		c++;
	}
	free(M);
	for(int i = 0; i < k; i++)
                free(p[i]);
        free(p);
	return 0;
}






/* double M[6][6] = {{4, 2, 3, 5, 1, 0}, {2, 3, 7, 8, 5, 2}, {5, 6, 7, 0, 9, 2}, {10, 6, 8, 3, 1, 1}, {5, 6, 7, 0, 0, 6}, {10, 6, 8, 3, 2, 3}};
    int L = 3;
    double **G = malloc(L*sizeof(double*));
    if (G==NULL) {fprintf(stderr, "ERROR: Memory could not be allocated.");}
    for (int i = 0; i<L; i++){
        G[i] = malloc(L*sizeof(double));
    }    

    gridificator(6, M, L, G);

    printf("les mitjanes son");
    printf("\n");
    for(int i = 0; i < L ;i++) {
        for(int j = 0; j < L; j++){
            printf( "%5.2lf ", G[i][j]);
        }
        printf("\n");
    }
    printf("\n");
*/
