package com.digitinary.dgate.model.monetization;

import com.fasterxml.jackson.annotation.JsonInclude;
import lombok.Data;
import lombok.NoArgsConstructor;
import java.time.LocalDateTime;
import java.util.Set;

/**
 * AssociatedResource.
 *
 * @author Raad khatatbeh
 * @since 7/08/2024
 */
@Data
@NoArgsConstructor
@JsonInclude(JsonInclude.Include.NON_NULL)
public class AssociatedResource {

    private String resourceId;
    private String objectType;
    private Set<String> publishedIn;
    private String resourceBody;
    private LocalDateTime publishedAt;
}
