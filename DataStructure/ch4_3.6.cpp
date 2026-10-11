void Parti(int A[], int n) {
    int left = 0, right = n - 1;
    while (left < right) {
        while (left < right && A[left] > 0)  left++;   // 找负数
        while (left < right && A[right] < 0) right--;  // 找正数
        if (left < right) { int t = A[left]; A[left] = A[right]; A[right] = t;
                            left++; right--; }
    }
}
