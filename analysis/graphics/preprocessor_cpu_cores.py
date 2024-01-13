import matplotlib.pyplot as plt
import templates

CORES = [1,2,4,8,12]
TIMES = [132.091, 85.243, 68.884, 60.039, 57.369]
def main():

	templates.template_style()
	fig, ax = plt.subplots()
	ax.plot(CORES, TIMES, label="PC1", marker="s")
	templates.template_plot(ax, "Execution Time (s)", "Cores Amount", "Preprocessor Scaling CPU Cores")
	templates.template_save_multiple_images([fig], "preprocessor_cpu_cores", ["preprocessor_cpu_cores"])
		
main()
