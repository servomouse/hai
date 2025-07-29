#include <stdio.h>
#include <math.h>

typedef struct {
    int n;                 // Count of pairs
    double sum_x;          // Sum of X values
    double sum_y;          // Sum of Y values
    double avg_delta_x;    // Average delta for X
    double avg_delta_y;    // Average delta for Y
    double avg_corr;       // Average correlation
} correlation_data_t;

// Function to initialize the calculator
void init_calculator(correlation_data_t *calc) {
    calc->n = 0;
    calc->sum_x = 0.0;
    calc->sum_y = 0.0;
    calc->avg_delta_x = 0.0;
    calc->avg_delta_y = 0.0;
    calc->avg_corr = 0.0;
}

// Function to update the calculator with new X and Y values
void update_calculator(correlation_data_t *calc, double x, double y) {
    calc->n++;
    calc->sum_x += x;
    calc->sum_y += y;

    double avg_x = (calc->n == 1) ? x : calc->sum_x / calc->n;
    double avg_y = (calc->n == 1) ? y : calc->sum_y / calc->n;

    double delta_x = round(x - avg_x);
    double delta_y = round(y - avg_y);

    if (delta_x == 0 && delta_y == 0) {
        if (calc->n > 1) {
            calc->avg_corr += 1; // Both deltas are zero
        }
    } else if (delta_x == 0 || delta_y == 0) {
        // Correlation remains unchanged
    } else {
        double temp_x = delta_x;
        if (calc->avg_delta_x != 0) {
            temp_x = delta_x / calc->avg_delta_x;
        }
        double temp_y = delta_y;
        if (calc->avg_delta_y != 0) {
            temp_y = delta_y / calc->avg_delta_y;
        }
        if (temp_x > temp_y) {
            calc->avg_corr += temp_y / temp_x;
        } else {
            calc->avg_corr += temp_x / temp_y;
        }
    }

    calc->avg_delta_x += fabs(delta_x);
    calc->avg_delta_y += fabs(delta_y);
}

double calculate_correlation(correlation_data_t *calc) {
    if (calc->n < 2) {
        return 0; // Not enough data to calculate correlation
    }
    return calc->avg_corr / (calc->n - 1); // First value doesn't count
}

// // Example usage
// int main() {
//     correlation_data_t calc;
//     init_calculator(&calc);

//     // Simulate updating with new values
//     update_calculator(&calc, 0.1, 0.0);
//     update_calculator(&calc, 0.0, 0.1);
//     update_calculator(&calc, 0.1, 0.0);
//     update_calculator(&calc, 0.0, 0.1);
//     update_calculator(&calc, 0.1, 0.0);
//     update_calculator(&calc, 0.0, 0.1);
//     update_calculator(&calc, 0.1, 0.0);
//     update_calculator(&calc, 0.0, 0.1);
//     update_calculator(&calc, 0.1, 0.0);
//     update_calculator(&calc, 0.0, 0.1);
    
//     double correlation = calculate_correlation(&calc);
//     printf("Correlation coefficient: %f\n", correlation);

//     return 0;
// }