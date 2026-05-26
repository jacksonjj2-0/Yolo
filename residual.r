

rm(list = ls())

# ---
# 1. Load data
# ---

hospital <- read.csv("hospital.csv")

str(hospital)
summary(hospital)

# ---
# 2. Convert categorical variables to factors
# ---

hospital$sex <- factor(hospital$sex)
hospital$antibiotic <- factor(hospital$antibiotic)
hospital$bculture <- factor(hospital$bculture)
hospital$service <- factor(hospital$service)

# ---
# Set reference categories
# ---

hospital$sex <- relevel(hospital$sex, ref = "female")
hospital$antibiotic <- relevel(hospital$antibiotic, ref = "no")
hospital$bculture <- relevel(hospital$bculture, ref = "no")
hospital$service <- relevel(hospital$service, ref = "med")

# ---
# 3. Fit full Gamma GLM with log link
# ---

gamma_log_full <- glm(
  duration ~ age + sex + temp + wbc + antibiotic + bculture + service,
  family = Gamma(link = "log"),
  data = hospital,
  control = glm.control(maxit = 100)
)

summary(gamma_log_full)

# ---
# 4. Final selected log-link model
# Backward selection was done at significance level 0.10
# Final retained variables: age and temp
# ---

gamma_log_final <- glm(
  duration ~ age + temp,
  family = Gamma(link = "log"),
  data = hospital,
  control = glm.control(maxit = 100)
)

summary(gamma_log_final)

# ---
# 5. Fit full Gamma GLM with identity link
# ---

gamma_id_full <- glm(
  duration ~ age + sex + temp + wbc + antibiotic + bculture + service,
  family = Gamma(link = "identity"),
  data = hospital,
  control = glm.control(maxit = 100)
)

summary(gamma_id_full)

# ---
# 6. Final selected identity-link model
# Backward selection was done at significance level 0.10
# Final retained variables: antibiotic and service
# ---

gamma_id_final <- glm(
  duration ~ antibiotic + service,
  family = Gamma(link = "identity"),
  data = hospital,
  control = glm.control(maxit = 100)
)

summary(gamma_id_final)

# ---
# 7. Compare final models
# Lower AIC and BIC indicate a better model
# ---

AIC(gamma_log_final, gamma_id_final)
BIC(gamma_log_final, gamma_id_final)

deviance(gamma_log_final)
deviance(gamma_id_final)

summary(gamma_log_final)$dispersion
summary(gamma_id_final)$dispersion

# ---
# 8. Create model comparison table
# ---

model_comparison <- data.frame(
  Model = c("Gamma log link", "Gamma identity link"),
  AIC = c(AIC(gamma_log_final), AIC(gamma_id_final)),
  BIC = c(BIC(gamma_log_final), BIC(gamma_id_final)),
  Deviance = c(deviance(gamma_log_final), deviance(gamma_id_final)),
  Dispersion = c(
    summary(gamma_log_final)$dispersion,
    summary(gamma_id_final)$dispersion
  )
)

print(model_comparison)

# ---
# 9. Check fitted values for identity-link model
# Gamma fitted means must be positive
# This check is especially important for the identity link
# ---

fitted_values_id <- fitted(gamma_id_final)

range(fitted_values_id)
print(fitted_values_id)

# ---
# 10. Diagnostic plots for the best model
# The best model is the identity-link Gamma GLM
# ---

par(mfrow = c(2, 2))
plot(gamma_id_final)

# ---
# 11. Residual checks
# ---

pearson_res <- residuals(gamma_id_final, type = "pearson")
deviance_res <- residuals(gamma_id_final, type = "deviance")

shapiro.test(pearson_res)
shapiro.test(deviance_res)

# ---
# 12. Quantile residuals for Gamma model
# Quantile residuals should be approximately normally distributed
# if the Gamma model is appropriate
# ---

phi_hat <- summary(gamma_id_final)$dispersion
mu_hat <- fitted(gamma_id_final)

shape_hat <- 1 / phi_hat
scale_hat <- mu_hat * phi_hat

quantile_res <- qnorm(
  pgamma(hospital$duration, shape = shape_hat, scale = scale_hat)
)

shapiro.test(quantile_res)

qqnorm(quantile_res)
qqline(quantile_res)

# ---
# 13. Check variance pattern
# If absolute residuals are strongly related to fitted values,
# there may be remaining heteroscedasticity
# ---

cor.test(
  abs(pearson_res),
  fitted(gamma_id_final),
  method = "spearman"
)

# ---
# 14. Check for large residuals or outliers
# ---

max(abs(pearson_res))

residual_table <- data.frame(
  duration = hospital$duration,
  fitted = fitted(gamma_id_final),
  pearson_residual = pearson_res,
  deviance_residual = deviance_res,
  quantile_residual = quantile_res
)

print(residual_table)

# ---
# 15. Estimated mean durations from final identity-link model
# ---

new_data <- expand.grid(
  antibiotic = levels(hospital$antibiotic),
  service = levels(hospital$service)
)

predicted_means <- predict(
  gamma_id_final,
  newdata = new_data,
  type = "response"
)

prediction_table <- data.frame(
  new_data,
  predicted_duration = predicted_means
)

print(prediction_table)

# ---
# 16. Check whether exponential distribution is suitable
# Exponential distribution is a special case of Gamma distribution
# where shape = 1
# For the Gamma GLM, shape = 1 / dispersion
# ---

phi_hat <- summary(gamma_id_final)$dispersion
shape_hat <- 1 / phi_hat

shape_hat

# ---
# 17. Likelihood ratio comparison
# Gamma model versus exponential restriction
# ---

ll_gamma <- as.numeric(logLik(gamma_id_final))

mu_hat <- fitted(gamma_id_final)

ll_exp <- sum(
  dexp(hospital$duration, rate = 1 / mu_hat, log = TRUE)
)

LR <- 2 * (ll_gamma - ll_exp)

p_value_exp <- pchisq(LR, df = 1, lower.tail = FALSE)

LR
p_value_exp

# ---
# 18. Print final model equations
# ---

cat("\nFinal Gamma log-link model:\n")
cat("log(mu_i) = -28.6539 + 0.01490 * age_i + 0.30662 * temp_i\n")
cat("mu_i = exp(-28.6539 + 0.01490 * age_i + 0.30662 * temp_i)\n")

cat("\nFinal Gamma identity-link model:\n")
cat("mu_i = 9.9246 + 4.1050 * I(antibiotic_i = yes) - 3.9161 * I(service_i = surg)\n")

