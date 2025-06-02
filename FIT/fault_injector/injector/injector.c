// injector/injector.c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

#define SYSFS_BASE "/sys/kernel/debug"

int write_sysfs(const char *path, const char *value) {
    FILE *f = fopen(path, "w");
    if (!f) {
        perror(path);
	printf("写入失败");
        return -1;
    }
    fprintf(f, "%s", value);
    //printf("写入成功");
    fclose(f);
    return 0;
}

int inject_common(const char *target,
                  int probability,
                  int interval,
                  int times,
                  int verbose,
                  int task_filter) {
    char base[256];
    snprintf(base, sizeof(base), SYSFS_BASE "/fail%s", target);

    char path[256], val[32];

    // probability
    snprintf(path, sizeof(path), "%s/probability", base);
    snprintf(val, sizeof(val), "%d", probability);
    write_sysfs(path, val);

    // interval
    snprintf(path, sizeof(path), "%s/interval", base);
    snprintf(val, sizeof(val), "%d", interval);
    write_sysfs(path, val);

    // times
    snprintf(path, sizeof(path), "%s/times", base);
    snprintf(val, sizeof(val), "%d", times);
    write_sysfs(path, val);

    // verbose
    snprintf(path, sizeof(path), "%s/verbose", base);
    snprintf(val, sizeof(val), "%d", verbose);
    write_sysfs(path, val);

    // task-filter
    if (task_filter > 0) {
        snprintf(path, sizeof(path), "%s/task-filter", base);
        snprintf(val, sizeof(val), "%d", task_filter);
        write_sysfs(path, val);
    }

    return 0;
}

// 特殊：fail_function 支持函数名注入
int inject_function(const char *func_name,
                    int probability,
                    int interval,
                    int times,
                    int verbose,
                    int task_filter) {
    char base[256], path[256], val[32];

    snprintf(base, sizeof(base), SYSFS_BASE "/fail_function");

    // func name
    snprintf(path, sizeof(path), "%s/func", base);
    write_sysfs(path, func_name);

    // 其余参数
    snprintf(path, sizeof(path), "%s/probability", base);
    snprintf(val, sizeof(val), "%d", probability);
    write_sysfs(path, val);

    snprintf(path, sizeof(path), "%s/interval", base);
    snprintf(val, sizeof(val), "%d", interval);
    write_sysfs(path, val);

    snprintf(path, sizeof(path), "%s/times", base);
    snprintf(val, sizeof(val), "%d", times);
    write_sysfs(path, val);

    snprintf(path, sizeof(path), "%s/verbose", base);
    snprintf(val, sizeof(val), "%d", verbose);
    write_sysfs(path, val);

    if (task_filter > 0) {
        snprintf(path, sizeof(path), "%s/task-filter", base);
        snprintf(val, sizeof(val), "%d", task_filter);
        write_sysfs(path, val);
    }

    return 0;
}

// 为 Python ctypes 显式暴露接口
int inject_pagealloc(int p, int i, int t, int v, int pid) {
    return inject_common("_page_alloc", p, i, t, v, pid);
}
int inject_slab(int p, int i, int t, int v, int pid) {
    return inject_common("slab", p, i, t, v, pid);
}
int inject_futex(int p, int i, int t, int v, int pid) {
    return inject_common("_futex", p, i, t, v, pid);
}
int inject_make_request(int p, int i, int t, int v, int pid) {
    return inject_common("_make_request", p, i, t, v, pid);
}
int inject_io_timeout(int p, int i, int t, int v, int pid) {
    return inject_common("_io_timeout", p, i, t, v, pid);
}
/*int main(){
	inject_pagealloc(66,1,33,2,0);
	return 0;
}*/
