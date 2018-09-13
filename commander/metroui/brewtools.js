function gravityTempAdjustment(intemp,gravity)
	caltemp=68;
	temp = ( intemp *1.8)+32
	answer = gravity * (1.00130346 - 1.34722124E-4 * temp + 2.04052596E-6 * temp * temp - 2.32820948E-9 * temp * temp * temp) / (1.00130346 - 1.34722124E-4 * caltemp + 2.04052596E-6 * caltemp * caltemp - 2.32820948E-9 * caltemp * caltemp * caltemp)
	return answer;
	


}

